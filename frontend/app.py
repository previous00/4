"""
招聘网站前端服务
运行方式: python app.py
访问地址: http://localhost:8080
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

HOST = '127.0.0.1'
PORT = 8080
API_BASE = 'http://127.0.0.1:5001/api'

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智聘网 - 在线招聘平台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f7fa; color: #333; }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 16px 32px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 { font-size: 24px; cursor: pointer; }
        .header-right { display: flex; gap: 12px; align-items: center; }
        .header-right span { font-size: 14px; }

        .btn {
            padding: 8px 16px; border: none; border-radius: 6px;
            cursor: pointer; font-size: 14px; transition: all 0.2s;
            display: inline-block;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5a6fd6; }
        .btn-success { background: #48bb78; color: white; }
        .btn-success:hover { background: #38a169; }
        .btn-danger { background: #f56565; color: white; }
        .btn-danger:hover { background: #e53e3e; }
        .btn-outline { background: transparent; border: 1px solid white; color: white; }
        .btn-outline:hover { background: rgba(255,255,255,0.15); }
        .btn-logout {
            background: rgba(255,80,80,0.3); border: 1px solid rgba(255,255,255,0.8);
            color: white; cursor: pointer; padding: 8px 16px; border-radius: 6px;
            font-size: 14px; transition: all 0.2s; position: relative; z-index: 10;
        }
        .btn-logout:hover { background: #e53e3e; border-color: #e53e3e; }
        .btn-sm { padding: 4px 10px; font-size: 12px; }

        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }

        .auth-modal {
            display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5); z-index: 1000;
            justify-content: center; align-items: center;
        }
        .auth-modal.active { display: flex; }
        .auth-box {
            background: white; padding: 32px; border-radius: 12px;
            width: 400px; max-width: 90%; position: relative;
        }
        .auth-box h2 { margin-bottom: 20px; color: #667eea; }

        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; margin-bottom: 6px; font-weight: 500; font-size: 14px; }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%; padding: 10px 12px; border: 1px solid #e2e8f0;
            border-radius: 6px; font-size: 14px; font-family: inherit;
        }
        .form-group textarea { height: 100px; resize: vertical; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }

        .tabs {
            display: flex; gap: 0; margin-bottom: 24px;
            border-bottom: 2px solid #e2e8f0;
        }
        .tab {
            padding: 12px 24px; cursor: pointer; font-weight: 500;
            border-bottom: 2px solid transparent; margin-bottom: -2px;
            transition: all 0.2s; user-select: none;
        }
        .tab.active { color: #667eea; border-bottom-color: #667eea; }
        .tab:hover { color: #667eea; }

        .search-bar {
            display: flex; gap: 12px; margin-bottom: 24px;
            background: white; padding: 16px; border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            flex-wrap: wrap;
        }
        .search-bar input, .search-bar select {
            padding: 10px 14px; border: 1px solid #e2e8f0;
            border-radius: 6px; font-size: 14px;
        }
        .search-bar input { flex: 1; min-width: 150px; }
        .search-bar select { min-width: 120px; }

        .job-list { display: grid; gap: 16px; }
        .job-card {
            background: white; padding: 20px; border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            cursor: pointer; transition: all 0.2s;
        }
        .job-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
        .job-card h3 { color: #2d3748; margin-bottom: 8px; }
        .job-card .meta {
            display: flex; gap: 16px; color: #718096; font-size: 13px;
            margin-bottom: 8px; flex-wrap: wrap;
        }
        .job-card .salary { color: #e53e3e; font-weight: 600; font-size: 16px; }
        .job-card .tags { display: flex; gap: 8px; margin-top: 8px; }
        .tag {
            background: #edf2f7; color: #4a5568; padding: 2px 8px;
            border-radius: 4px; font-size: 12px;
        }

        .detail-panel {
            display: none; position: fixed; top: 0; right: 0; bottom: 0;
            width: 520px; max-width: 92%; background: white;
            box-shadow: -4px 0 20px rgba(0,0,0,0.15); z-index: 100;
            overflow-y: auto; padding: 32px;
        }
        .detail-panel.active { display: block; }
        .detail-panel h2 { margin-bottom: 16px; padding-right: 30px; }
        .detail-section { margin-bottom: 20px; }
        .detail-section h4 { color: #667eea; margin-bottom: 8px; font-size: 15px; }
        .detail-section p { line-height: 1.7; color: #4a5568; font-size: 14px; }

        .overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); z-index: 99; }
        .overlay.active { display: block; }

        .page-section { display: none; }
        .page-section.active { display: block; }

        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
        th, td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #edf2f7; font-size: 14px; }
        th { background: #f7fafc; font-weight: 600; color: #4a5568; }

        .status-badge {
            display: inline-block; padding: 2px 8px; border-radius: 4px;
            font-size: 12px; font-weight: 500;
        }
        .status-pending { background: #fefcbf; color: #975a16; }
        .status-viewed { background: #bee3f8; color: #2a4365; }
        .status-accepted { background: #c6f6d5; color: #276749; }
        .status-rejected { background: #fed7d7; color: #9b2c2c; }
        .status-open { background: #c6f6d5; color: #276749; }
        .status-closed { background: #fed7d7; color: #9b2c2c; }
        .status-paused { background: #fefcbf; color: #975a16; }

        .pagination { display: flex; gap: 8px; justify-content: center; margin-top: 24px; }
        .pagination button {
            padding: 6px 12px; border: 1px solid #e2e8f0; background: white;
            border-radius: 4px; cursor: pointer; font-size: 13px;
        }
        .pagination button.active { background: #667eea; color: white; border-color: #667eea; }
        .pagination button:hover { border-color: #667eea; }

        .empty { text-align: center; padding: 60px 20px; color: #a0aec0; }
        .empty p { font-size: 16px; }

        .close-btn {
            position: absolute; top: 16px; right: 16px; font-size: 24px;
            cursor: pointer; color: #a0aec0; background: none; border: none;
            width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
            border-radius: 50%;
        }
        .close-btn:hover { color: #333; background: #f0f0f0; }

        .toast {
            position: fixed; top: 20px; right: 20px; z-index: 2000;
            padding: 12px 20px; border-radius: 8px; color: white;
            font-size: 14px; opacity: 0; transition: opacity 0.3s;
            max-width: 350px;
        }
        .toast.show { opacity: 1; }
        .toast.success { background: #48bb78; }
        .toast.error { background: #f56565; }
        .toast.info { background: #4299e1; }

        .loading {
            text-align: center; padding: 40px; color: #a0aec0;
        }
    </style>
</head>
<body>

<div class="header">
    <h1 onclick="switchPage('jobs')">智聘网</h1>
    <div class="header-right" id="headerRight">
        <button class="btn btn-outline" onclick="showAuth('login')">登录</button>
        <button class="btn btn-outline" onclick="showAuth('register')">注册</button>
    </div>
</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<!-- Auth Modal -->
<div class="auth-modal" id="authModal">
    <div class="auth-box">
        <button class="close-btn" onclick="hideAuth()">&times;</button>
        <h2 id="authTitle">登录</h2>
        <div id="authForm">
            <div class="form-group">
                <label>用户名</label>
                <input type="text" id="authUsername" placeholder="请输入用户名">
            </div>
            <div class="form-group">
                <label>密码</label>
                <input type="password" id="authPassword" placeholder="请输入密码">
            </div>
            <div class="form-group" id="roleGroup" style="display:none">
                <label>注册身份</label>
                <select id="authRole">
                    <option value="jobseeker">求职者</option>
                    <option value="company">企业用户</option>
                </select>
            </div>
            <button class="btn btn-primary" style="width:100%;padding:12px" id="authSubmit" onclick="submitAuth()">登录</button>
            <p style="text-align:center;margin-top:12px;font-size:13px;color:#718096" id="authSwitchWrap"></p>
        </div>
    </div>
</div>

<!-- Main Content -->
<div class="container">
    <div class="tabs" id="mainTabs">
        <div class="tab active" data-page="jobs" onclick="switchPage('jobs')">职位搜索</div>
    </div>

    <!-- Jobs Page -->
    <div class="page-section active" id="page-jobs">
        <div class="search-bar">
            <input type="text" id="searchKeyword" placeholder="搜索职位关键词..." onkeydown="if(event.key==='Enter')searchJobs()">
            <select id="searchCategory">
                <option value="">全部分类</option>
            </select>
            <input type="text" id="searchLocation" placeholder="工作地点" onkeydown="if(event.key==='Enter')searchJobs()">
            <button class="btn btn-primary" onclick="searchJobs()">搜索</button>
        </div>
        <div class="job-list" id="jobList">
            <div class="loading">加载中...</div>
        </div>
        <div class="pagination" id="pagination"></div>
    </div>

    <!-- Profile Page -->
    <div class="page-section" id="page-profile"></div>

    <!-- My Applications Page -->
    <div class="page-section" id="page-applications"></div>

    <!-- Post Job Page -->
    <div class="page-section" id="page-post-job"></div>

    <!-- My Jobs Page -->
    <div class="page-section" id="page-my-jobs"></div>

    <!-- Received Resumes Page -->
    <div class="page-section" id="page-resumes"></div>
</div>

<!-- Job Detail Panel -->
<div class="overlay" id="overlay" onclick="closeDetail()"></div>
<div class="detail-panel" id="detailPanel">
    <button class="close-btn" onclick="closeDetail()">&times;</button>
    <div id="detailContent"></div>
</div>

<script>
// ==================== 配置 ====================
const API = '{{API_BASE}}';
let token = localStorage.getItem('token');
let currentUser = null;
let currentPage = 1;
let authMode = 'login';

// 页面加载时恢复用户状态
try {
    currentUser = JSON.parse(localStorage.getItem('user'));
} catch(e) {
    currentUser = null;
}

function headers(isJson) {
    const h = {};
    if (isJson !== false) h['Content-Type'] = 'application/json';
    if (token) h['Authorization'] = 'Bearer ' + token;
    return h;
}

// ==================== Toast 提示 ====================

function showToast(msg, type) {
    type = type || 'info';
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast ' + type + ' show';
    setTimeout(function() { el.className = 'toast'; }, 3000);
}

// ==================== 网络请求封装 ====================

async function apiRequest(url, options) {
    options = options || {};
    try {
        var res = await fetch(url, options);
        var data = await res.json();
        if (!res.ok) {
            var errMsg = data.error || data.msg || '请求失败(' + res.status + ')';
            showToast(errMsg, 'error');
            return null;
        }
        return data;
    } catch(e) {
        showToast('网络错误，请确保后端服务已启动 (端口5001)', 'error');
        console.error('API Error:', e);
        return null;
    }
}

// ==================== 认证 ====================

function showAuth(mode) {
    authMode = mode;
    document.getElementById('authModal').classList.add('active');
    document.getElementById('authTitle').textContent = mode === 'login' ? '登录' : '注册';
    document.getElementById('roleGroup').style.display = mode === 'register' ? 'block' : 'none';
    document.getElementById('authSubmit').textContent = mode === 'login' ? '登录' : '注册';
    document.getElementById('authSwitchWrap').innerHTML = mode === 'login'
        ? '没有账号？<a href="javascript:void(0)" onclick="showAuth(\'register\')">立即注册</a>'
        : '已有账号？<a href="javascript:void(0)" onclick="showAuth(\'login\')">立即登录</a>';
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
    document.getElementById('authUsername').focus();
}

function hideAuth() {
    document.getElementById('authModal').classList.remove('active');
}

async function submitAuth() {
    var username = document.getElementById('authUsername').value.trim();
    var password = document.getElementById('authPassword').value.trim();
    var role = document.getElementById('authRole').value;

    if (!username || !password) {
        showToast('请填写用户名和密码', 'error');
        return;
    }
    if (username.length < 2) {
        showToast('用户名至少2个字符', 'error');
        return;
    }
    if (password.length < 4) {
        showToast('密码至少4个字符', 'error');
        return;
    }

    var url = authMode === 'login' ? API + '/auth/login' : API + '/auth/register';
    var body = authMode === 'login' ? {username: username, password: password} : {username: username, password: password, role: role};

    var data = await apiRequest(url, {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(body)
    });

    if (data) {
        token = data.token;
        currentUser = data.user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(currentUser));
        hideAuth();
        renderUI();
        showToast(authMode === 'login' ? '登录成功' : '注册成功', 'success');
        searchJobs();
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    renderUI();
    switchPage('jobs');
    showToast('已退出登录', 'info');
    searchJobs();
}

// ==================== UI渲染 ====================

function renderUI() {
    var right = document.getElementById('headerRight');
    var tabs = document.getElementById('mainTabs');

    if (currentUser) {
        var roleName = currentUser.role === 'company' ? '企业' : '求职者';
        var displayName = currentUser.company_name || currentUser.real_name || currentUser.username;
        right.innerHTML = '<span>' + esc(displayName) + ' (' + roleName + ')</span>' +
            '<button class="btn-logout" id="logoutBtn">退出登录</button>';
        document.getElementById('logoutBtn').addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            logout();
        });

        if (currentUser.role === 'jobseeker') {
            tabs.innerHTML =
                '<div class="tab active" data-page="jobs" onclick="switchPage(\'jobs\')">职位搜索</div>' +
                '<div class="tab" data-page="profile" onclick="switchPage(\'profile\')">个人资料</div>' +
                '<div class="tab" data-page="applications" onclick="switchPage(\'applications\')">投递记录</div>';
        } else {
            tabs.innerHTML =
                '<div class="tab active" data-page="jobs" onclick="switchPage(\'jobs\')">职位搜索</div>' +
                '<div class="tab" data-page="profile" onclick="switchPage(\'profile\')">企业资料</div>' +
                '<div class="tab" data-page="post-job" onclick="switchPage(\'post-job\')">发布职位</div>' +
                '<div class="tab" data-page="my-jobs" onclick="switchPage(\'my-jobs\')">我的职位</div>' +
                '<div class="tab" data-page="resumes" onclick="switchPage(\'resumes\')">收到的简历</div>';
        }
    } else {
        right.innerHTML =
            '<button class="btn btn-outline" onclick="showAuth(\'login\')">登录</button>' +
            '<button class="btn btn-outline" onclick="showAuth(\'register\')">注册</button>';
        tabs.innerHTML = '<div class="tab active" data-page="jobs" onclick="switchPage(\'jobs\')">职位搜索</div>';
    }
}

function switchPage(page) {
    document.querySelectorAll('.page-section').forEach(function(el) { el.classList.remove('active'); });
    document.querySelectorAll('.tab').forEach(function(el) { el.classList.remove('active'); });

    var pageEl = document.getElementById('page-' + page);
    if (pageEl) pageEl.classList.add('active');

    var tabEl = document.querySelector('.tab[data-page="' + page + '"]');
    if (tabEl) tabEl.classList.add('active');

    if (page === 'profile') loadProfile();
    else if (page === 'applications') loadApplications();
    else if (page === 'post-job') renderPostJob();
    else if (page === 'my-jobs') loadMyJobs();
    else if (page === 'resumes') loadResumes();
    else if (page === 'jobs') searchJobs();
}

// ==================== 职位搜索 ====================

async function loadCategories() {
    var data = await apiRequest(API + '/categories', { method: 'GET' });
    if (data) {
        var select = document.getElementById('searchCategory');
        select.innerHTML = '<option value="">全部分类</option>';
        data.forEach(function(c) {
            var opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            select.appendChild(opt);
        });
    }
}

async function searchJobs(page) {
    page = page || 1;
    currentPage = page;
    var keyword = document.getElementById('searchKeyword').value;
    var category = document.getElementById('searchCategory').value;
    var location = document.getElementById('searchLocation').value;

    var params = new URLSearchParams({keyword: keyword, category: category, location: location, page: page, per_page: 10});

    var data = await apiRequest(API + '/jobs?' + params.toString(), { method: 'GET' });
    var list = document.getElementById('jobList');

    if (!data) {
        list.innerHTML = '<div class="empty"><p>无法加载职位列表，请确认后端已启动</p></div>';
        return;
    }

    if (data.jobs.length === 0) {
        list.innerHTML = '<div class="empty"><p>暂无匹配的职位</p></div>';
    } else {
        list.innerHTML = data.jobs.map(function(job) {
            var salary = (job.salary_min && job.salary_max) ? job.salary_min + '-' + job.salary_max + 'K' : '薪资面议';
            return '<div class="job-card" onclick="showJobDetail(' + job.id + ')">' +
                '<h3>' + esc(job.title) + '</h3>' +
                '<div class="meta">' +
                    '<span>' + esc(job.company_name) + '</span>' +
                    '<span>' + esc(job.location || '未指定地点') + '</span>' +
                    '<span>' + esc(job.experience_req || '经验不限') + '</span>' +
                    '<span>' + esc(job.education_req || '学历不限') + '</span>' +
                '</div>' +
                '<div class="salary">' + salary + '</div>' +
                '<div class="tags"><span class="tag">' + esc(job.category) + '</span></div>' +
            '</div>';
        }).join('');
    }

    renderPagination(data.pages, data.current_page);
}

function renderPagination(totalPages, current) {
    var el = document.getElementById('pagination');
    if (totalPages <= 1) { el.innerHTML = ''; return; }
    var html = '';
    for (var i = 1; i <= totalPages; i++) {
        html += '<button class="' + (i === current ? 'active' : '') + '" onclick="searchJobs(' + i + ')">' + i + '</button>';
    }
    el.innerHTML = html;
}

async function showJobDetail(id) {
    var job = await apiRequest(API + '/jobs/' + id, { method: 'GET' });
    if (!job) return;

    var salary = (job.salary_min && job.salary_max) ? job.salary_min + '-' + job.salary_max + 'K' : '薪资面议';

    var applySection = '';
    if (currentUser && currentUser.role === 'jobseeker') {
        applySection = '<hr style="margin:20px 0">' +
            '<div class="form-group">' +
                '<label>求职信（可选）</label>' +
                '<textarea id="coverLetter" placeholder="写一封简短的求职信介绍自己..."></textarea>' +
            '</div>' +
            '<button class="btn btn-success" style="width:100%;padding:12px;font-size:16px" onclick="applyJob(' + job.id + ')">投递简历</button>';
    } else if (!currentUser) {
        applySection = '<hr style="margin:20px 0"><p style="color:#718096;text-align:center">请<a href="javascript:void(0)" onclick="closeDetail();showAuth(\'login\')">登录</a>后投递简历</p>';
    }

    document.getElementById('detailContent').innerHTML =
        '<h2>' + esc(job.title) + '</h2>' +
        '<div class="salary" style="font-size:20px;margin-bottom:16px">' + salary + '</div>' +
        '<div class="detail-section"><h4>公司信息</h4>' +
            '<p><strong>' + esc(job.company_name) + '</strong></p>' +
            '<p>' + esc(job.company_desc || '暂无公司介绍') + '</p></div>' +
        '<div class="detail-section"><h4>基本信息</h4>' +
            '<p>工作地点：' + esc(job.location || '未指定') + '</p>' +
            '<p>经验要求：' + esc(job.experience_req || '不限') + '</p>' +
            '<p>学历要求：' + esc(job.education_req || '不限') + '</p>' +
            '<p>职位分类：' + esc(job.category) + '</p></div>' +
        '<div class="detail-section"><h4>职位描述</h4>' +
            '<p>' + esc(job.description).replace(/\n/g, '<br>') + '</p></div>' +
        '<div class="detail-section"><h4>任职要求</h4>' +
            '<p>' + esc(job.requirements || '无特殊要求').replace(/\n/g, '<br>') + '</p></div>' +
        applySection;

    document.getElementById('overlay').classList.add('active');
    document.getElementById('detailPanel').classList.add('active');
}

function closeDetail() {
    document.getElementById('overlay').classList.remove('active');
    document.getElementById('detailPanel').classList.remove('active');
}

async function applyJob(jobId) {
    var coverLetter = document.getElementById('coverLetter').value;
    var data = await apiRequest(API + '/applications', {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({ job_id: jobId, cover_letter: coverLetter })
    });
    if (data) {
        showToast('投递成功！', 'success');
        closeDetail();
    }
}

// ==================== 个人资料 ====================

function loadProfile() {
    var el = document.getElementById('page-profile');
    if (!currentUser) return;

    if (currentUser.role === 'jobseeker') {
        el.innerHTML =
            '<div style="background:white;padding:24px;border-radius:10px;max-width:600px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">' +
                '<h3 style="margin-bottom:20px">个人资料</h3>' +
                '<div class="form-group"><label>姓名</label><input id="pName" value="' + esc(currentUser.real_name || '') + '"></div>' +
                '<div class="form-group"><label>手机</label><input id="pPhone" value="' + esc(currentUser.phone || '') + '"></div>' +
                '<div class="form-group"><label>邮箱</label><input id="pEmail" type="email" value="' + esc(currentUser.email || '') + '"></div>' +
                '<div class="form-group"><label>学历</label><input id="pEducation" value="' + esc(currentUser.education || '') + '" placeholder="如：本科/硕士"></div>' +
                '<div class="form-group"><label>工作经验</label><textarea id="pExperience" placeholder="描述您的工作经历...">' + esc(currentUser.experience || '') + '</textarea></div>' +
                '<div class="form-group"><label>技能</label><textarea id="pSkills" placeholder="列出您的技能...">' + esc(currentUser.skills || '') + '</textarea></div>' +
                '<button class="btn btn-primary" onclick="saveProfile()">保存资料</button>' +
                '<hr style="margin:24px 0">' +
                '<h4 style="margin-bottom:12px">上传简历</h4>' +
                '<p style="font-size:13px;color:#718096;margin-bottom:8px">当前简历：' + (currentUser.resume_path ? '<span style="color:#48bb78">已上传</span>' : '<span style="color:#e53e3e">未上传</span>') + '</p>' +
                '<input type="file" id="resumeFile" accept=".pdf,.doc,.docx">' +
                '<button class="btn btn-success" style="margin-top:8px;margin-left:8px" onclick="uploadResume()">上传</button>' +
                '<p style="font-size:12px;color:#a0aec0;margin-top:4px">支持 PDF、DOC、DOCX 格式</p>' +
            '</div>';
    } else {
        el.innerHTML =
            '<div style="background:white;padding:24px;border-radius:10px;max-width:600px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">' +
                '<h3 style="margin-bottom:20px">企业资料</h3>' +
                '<div class="form-group"><label>公司名称</label><input id="pCompanyName" value="' + esc(currentUser.company_name || '') + '"></div>' +
                '<div class="form-group"><label>公司地址</label><input id="pCompanyAddr" value="' + esc(currentUser.company_address || '') + '"></div>' +
                '<div class="form-group"><label>公司网站</label><input id="pCompanyWeb" value="' + esc(currentUser.company_website || '') + '" placeholder="https://"></div>' +
                '<div class="form-group"><label>公司简介</label><textarea id="pCompanyDesc" placeholder="介绍公司业务和文化...">' + esc(currentUser.company_desc || '') + '</textarea></div>' +
                '<button class="btn btn-primary" onclick="saveProfile()">保存资料</button>' +
            '</div>';
    }
}

async function saveProfile() {
    var body;
    if (currentUser.role === 'jobseeker') {
        body = {
            real_name: document.getElementById('pName').value,
            phone: document.getElementById('pPhone').value,
            email: document.getElementById('pEmail').value,
            education: document.getElementById('pEducation').value,
            experience: document.getElementById('pExperience').value,
            skills: document.getElementById('pSkills').value
        };
    } else {
        body = {
            company_name: document.getElementById('pCompanyName').value,
            company_desc: document.getElementById('pCompanyDesc').value,
            company_address: document.getElementById('pCompanyAddr').value,
            company_website: document.getElementById('pCompanyWeb').value
        };
    }

    var data = await apiRequest(API + '/profile', {
        method: 'PUT',
        headers: headers(),
        body: JSON.stringify(body)
    });

    if (data) {
        currentUser = data;
        localStorage.setItem('user', JSON.stringify(currentUser));
        renderUI();
        showToast('资料保存成功', 'success');
    }
}

async function uploadResume() {
    var fileInput = document.getElementById('resumeFile');
    var file = fileInput.files[0];
    if (!file) {
        showToast('请先选择文件', 'error');
        return;
    }

    var formData = new FormData();
    formData.append('resume', file);

    var data = await apiRequest(API + '/profile/resume', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: formData
    });

    if (data) {
        currentUser.resume_path = data.filename;
        localStorage.setItem('user', JSON.stringify(currentUser));
        showToast('简历上传成功', 'success');
        loadProfile();
    }
}

// ==================== 投递记录 ====================

async function loadApplications() {
    var el = document.getElementById('page-applications');
    el.innerHTML = '<div class="loading">加载中...</div>';

    var apps = await apiRequest(API + '/applications/my', { method: 'GET', headers: headers() });
    if (!apps) { el.innerHTML = '<div class="empty"><p>加载失败</p></div>'; return; }

    if (apps.length === 0) {
        el.innerHTML = '<div class="empty"><p>暂无投递记录，去搜索心仪的职位吧！</p></div>';
        return;
    }

    el.innerHTML = '<div class="table-wrap"><table>' +
        '<thead><tr><th>职位</th><th>公司</th><th>投递时间</th><th>状态</th></tr></thead>' +
        '<tbody>' + apps.map(function(a) {
            return '<tr>' +
                '<td>' + esc(a.job_title) + '</td>' +
                '<td>' + esc(a.company_name) + '</td>' +
                '<td>' + formatDate(a.created_at) + '</td>' +
                '<td><span class="status-badge status-' + a.status + '">' + statusText(a.status) + '</span></td>' +
            '</tr>';
        }).join('') +
        '</tbody></table></div>';
}

// ==================== 发布职位 ====================

function renderPostJob() {
    document.getElementById('page-post-job').innerHTML =
        '<div style="background:white;padding:24px;border-radius:10px;max-width:700px;box-shadow:0 2px 8px rgba(0,0,0,0.06)">' +
            '<h3 style="margin-bottom:20px">发布新职位</h3>' +
            '<div class="form-group"><label>职位名称 *</label><input id="jTitle" placeholder="如：前端开发工程师"></div>' +
            '<div class="form-group"><label>职位分类 *</label>' +
                '<select id="jCategory">' +
                    '<option value="技术开发">技术开发</option>' +
                    '<option value="产品设计">产品设计</option>' +
                    '<option value="市场营销">市场营销</option>' +
                    '<option value="运营管理">运营管理</option>' +
                    '<option value="人力资源">人力资源</option>' +
                    '<option value="财务会计">财务会计</option>' +
                    '<option value="行政后勤">行政后勤</option>' +
                    '<option value="销售客服">销售客服</option>' +
                '</select></div>' +
            '<div class="form-group"><label>工作地点</label><input id="jLocation" placeholder="如：北京 / 上海 / 远程"></div>' +
            '<div style="display:flex;gap:12px">' +
                '<div class="form-group" style="flex:1"><label>最低薪资(K/月)</label><input type="number" id="jSalaryMin" placeholder="如：15" min="0"></div>' +
                '<div class="form-group" style="flex:1"><label>最高薪资(K/月)</label><input type="number" id="jSalaryMax" placeholder="如：30" min="0"></div>' +
            '</div>' +
            '<div style="display:flex;gap:12px">' +
                '<div class="form-group" style="flex:1"><label>经验要求</label><input id="jExp" placeholder="如：3-5年"></div>' +
                '<div class="form-group" style="flex:1"><label>学历要求</label><input id="jEdu" placeholder="如：本科"></div>' +
            '</div>' +
            '<div class="form-group"><label>职位描述 *</label><textarea id="jDesc" placeholder="详细描述工作内容和职责..."></textarea></div>' +
            '<div class="form-group"><label>任职要求</label><textarea id="jReq" placeholder="列出技术要求和能力要求..."></textarea></div>' +
            '<button class="btn btn-success" style="padding:12px 32px;font-size:15px" onclick="postJob()">发布职位</button>' +
        '</div>';
}

async function postJob() {
    var title = document.getElementById('jTitle').value.trim();
    var description = document.getElementById('jDesc').value.trim();
    var category = document.getElementById('jCategory').value;

    if (!title) { showToast('请填写职位名称', 'error'); return; }
    if (!description) { showToast('请填写职位描述', 'error'); return; }

    var body = {
        title: title,
        category: category,
        location: document.getElementById('jLocation').value.trim(),
        salary_min: parseInt(document.getElementById('jSalaryMin').value) || null,
        salary_max: parseInt(document.getElementById('jSalaryMax').value) || null,
        experience_req: document.getElementById('jExp').value.trim(),
        education_req: document.getElementById('jEdu').value.trim(),
        description: description,
        requirements: document.getElementById('jReq').value.trim()
    };

    var data = await apiRequest(API + '/jobs', {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify(body)
    });

    if (data) {
        showToast('职位发布成功！', 'success');
        switchPage('my-jobs');
    }
}

// ==================== 我的职位 ====================

async function loadMyJobs() {
    var el = document.getElementById('page-my-jobs');
    el.innerHTML = '<div class="loading">加载中...</div>';

    var jobs = await apiRequest(API + '/company/jobs', { method: 'GET', headers: headers() });
    if (!jobs) { el.innerHTML = '<div class="empty"><p>加载失败</p></div>'; return; }

    if (jobs.length === 0) {
        el.innerHTML = '<div class="empty"><p>暂无已发布的职位，去发布第一个职位吧！</p></div>';
        return;
    }

    el.innerHTML = '<div class="table-wrap"><table>' +
        '<thead><tr><th>职位名称</th><th>分类</th><th>地点</th><th>薪资</th><th>状态</th><th>操作</th></tr></thead>' +
        '<tbody>' + jobs.map(function(j) {
            var salary = (j.salary_min && j.salary_max) ? j.salary_min + '-' + j.salary_max + 'K' : '面议';
            var statusHtml = '<span class="status-badge status-' + j.status + '">' +
                (j.status === 'open' ? '招聘中' : j.status === 'closed' ? '已关闭' : '暂停') + '</span>';
            return '<tr>' +
                '<td>' + esc(j.title) + '</td>' +
                '<td>' + esc(j.category) + '</td>' +
                '<td>' + esc(j.location || '-') + '</td>' +
                '<td>' + salary + '</td>' +
                '<td>' + statusHtml + '</td>' +
                '<td><select onchange="updateJobStatus(' + j.id + ', this.value)" style="padding:4px 8px;border-radius:4px;border:1px solid #e2e8f0;font-size:13px">' +
                    '<option value="open"' + (j.status === 'open' ? ' selected' : '') + '>招聘中</option>' +
                    '<option value="paused"' + (j.status === 'paused' ? ' selected' : '') + '>暂停</option>' +
                    '<option value="closed"' + (j.status === 'closed' ? ' selected' : '') + '>关闭</option>' +
                '</select></td>' +
            '</tr>';
        }).join('') +
        '</tbody></table></div>';
}

async function updateJobStatus(jobId, status) {
    var data = await apiRequest(API + '/jobs/' + jobId, {
        method: 'PUT',
        headers: headers(),
        body: JSON.stringify({ status: status })
    });
    if (data) {
        showToast('状态已更新', 'success');
        loadMyJobs();
    }
}

// ==================== 收到的简历 ====================

async function loadResumes() {
    var el = document.getElementById('page-resumes');
    el.innerHTML = '<div class="loading">加载中...</div>';

    var apps = await apiRequest(API + '/applications/received', { method: 'GET', headers: headers() });
    if (!apps) { el.innerHTML = '<div class="empty"><p>加载失败</p></div>'; return; }

    if (apps.length === 0) {
        el.innerHTML = '<div class="empty"><p>暂无收到的简历</p></div>';
        return;
    }

    el.innerHTML = '<div class="table-wrap"><table>' +
        '<thead><tr><th>求职者</th><th>投递职位</th><th>学历</th><th>技能</th><th>时间</th><th>状态</th><th>操作</th></tr></thead>' +
        '<tbody>' + apps.map(function(a) {
            return '<tr>' +
                '<td><strong>' + esc(a.applicant_name) + '</strong>' +
                    (a.applicant_email ? '<br><small style="color:#718096">' + esc(a.applicant_email) + '</small>' : '') +
                    (a.applicant_phone ? '<br><small style="color:#718096">' + esc(a.applicant_phone) + '</small>' : '') +
                '</td>' +
                '<td>' + esc(a.job_title) + '</td>' +
                '<td>' + esc(a.applicant_education || '-') + '</td>' +
                '<td>' + esc(a.applicant_skills || '-') + '</td>' +
                '<td>' + formatDate(a.created_at) + '</td>' +
                '<td><span class="status-badge status-' + a.status + '">' + statusText(a.status) + '</span></td>' +
                '<td><select onchange="updateAppStatus(' + a.id + ', this.value)" style="padding:4px 8px;border-radius:4px;border:1px solid #e2e8f0;font-size:13px">' +
                    '<option value="pending"' + (a.status === 'pending' ? ' selected' : '') + '>待处理</option>' +
                    '<option value="viewed"' + (a.status === 'viewed' ? ' selected' : '') + '>已查看</option>' +
                    '<option value="accepted"' + (a.status === 'accepted' ? ' selected' : '') + '>通过</option>' +
                    '<option value="rejected"' + (a.status === 'rejected' ? ' selected' : '') + '>拒绝</option>' +
                '</select></td>' +
            '</tr>';
        }).join('') +
        '</tbody></table></div>';
}

async function updateAppStatus(appId, status) {
    var data = await apiRequest(API + '/applications/' + appId + '/status', {
        method: 'PUT',
        headers: headers(),
        body: JSON.stringify({ status: status })
    });
    if (data) {
        showToast('状态已更新', 'success');
        loadResumes();
    }
}

// ==================== 工具函数 ====================

function statusText(s) {
    var map = { pending: '待处理', viewed: '已查看', accepted: '已通过', rejected: '已拒绝' };
    return map[s] || s;
}

function formatDate(isoStr) {
    if (!isoStr) return '-';
    var d = new Date(isoStr);
    return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
}

function esc(str) {
    if (str === null || str === undefined) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(String(str)));
    return div.innerHTML;
}

// ==================== 初始化 ====================

renderUI();
loadCategories();
searchJobs();
</script>
</body>
</html>'''


class FrontendHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        content = HTML_CONTENT.replace('{{API_BASE}}', API_BASE)
        self.wfile.write(content.encode('utf-8'))

    def log_message(self, format, *args):
        print(f"[前端] {args[0]}")


def main():
    server = HTTPServer((HOST, PORT), FrontendHandler)
    print("=" * 50)
    print("  智聘网 - 前端服务")
    print("=" * 50)
    print(f"  前端地址: http://{HOST}:{PORT}")
    print(f"  后端地址: {API_BASE}")
    print()
    print("  请确保后端服务已启动 (python backend/app.py)")
    print("  按 Ctrl+C 停止服务")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n前端服务已停止")
        server.server_close()


if __name__ == '__main__':
    main()

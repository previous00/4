# 智聘网 - 在线招聘平台

前后端分离的招聘业务系统，使用 REST API 接口。

## 技术栈

- **后端**：Python Flask + SQLAlchemy + SQLite + JWT 认证
- **前端**：Python HTTP 服务 + 原生 HTML/CSS/JavaScript
- **API**：RESTful 风格接口

## 项目结构

```
├── venv/                # Python 虚拟环境
├── backend/
│   ├── app.py           # 后端 API 服务 (端口 5001)
│   └── uploads/         # 简历上传目录
├── frontend/
│   └── app.py           # 前端服务 (端口 8080)
├── requirements.txt     # Python 依赖
└── README.md
```

## 启动方式

### 1. 激活虚拟环境

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖（首次）

```bash
pip install -r requirements.txt
```

### 3. 启动后端（打开第一个终端）

```bash
cd backend
python app.py
```

后端运行在 http://localhost:5001

### 4. 启动前端（打开第二个终端）

```bash
cd frontend
python app.py
```

前端运行在 http://localhost:8080

### 5. 访问网站

浏览器打开 http://localhost:8080

## 功能说明

### 求职者功能
- 注册/登录账号
- 维护个人资料（姓名、手机、邮箱、学历、经验、技能）
- 上传简历（PDF/DOC/DOCX）
- 搜索职位（关键词、分类、地点筛选）
- 查看职位详情
- 投递简历并附加求职信
- 查看投递历史和状态

### 企业用户功能
- 注册/登录账号
- 维护企业资料（公司名、地址、网站、简介）
- 发布职位（名称、分类、薪资、要求等）
- 管理职位状态（招聘中/暂停/关闭）
- 查看收到的简历列表
- 更新简历处理状态（待处理/已查看/通过/拒绝）

## API 接口

| 方法   | 路径                          | 说明         |
|--------|-------------------------------|--------------|
| POST   | /api/auth/register            | 用户注册     |
| POST   | /api/auth/login               | 用户登录     |
| GET    | /api/profile                  | 获取个人资料 |
| PUT    | /api/profile                  | 更新个人资料 |
| POST   | /api/profile/resume           | 上传简历     |
| GET    | /api/jobs                     | 职位列表/搜索|
| GET    | /api/jobs/:id                 | 职位详情     |
| POST   | /api/jobs                     | 发布职位     |
| PUT    | /api/jobs/:id                 | 编辑职位     |
| DELETE | /api/jobs/:id                 | 删除职位     |
| GET    | /api/company/jobs             | 企业职位列表 |
| POST   | /api/applications             | 投递职位     |
| GET    | /api/applications/my          | 我的投递记录 |
| GET    | /api/applications/received    | 收到的简历   |
| PUT    | /api/applications/:id/status  | 更新投递状态 |
| GET    | /api/categories               | 获取分类列表 |

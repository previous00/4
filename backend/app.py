from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recruitment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'recruitment-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== Models ====================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'jobseeker' or 'company'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Jobseeker fields
    real_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    education = db.Column(db.String(50))
    experience = db.Column(db.Text)
    skills = db.Column(db.Text)
    resume_path = db.Column(db.String(200))

    # Company fields
    company_name = db.Column(db.String(100))
    company_desc = db.Column(db.Text)
    company_address = db.Column(db.String(200))
    company_website = db.Column(db.String(200))


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    experience_req = db.Column(db.String(50))
    education_req = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    status = db.Column(db.String(20), default='open')  # open, closed, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company = db.relationship('User', backref='jobs')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, viewed, accepted, rejected
    cover_letter = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    job = db.relationship('Job', backref='applications')
    applicant = db.relationship('User', backref='applications')


# ==================== Auth APIs ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({'error': '用户名、密码和角色不能为空'}), 400

    if role not in ('jobseeker', 'company'):
        return jsonify({'error': '角色必须是 jobseeker 或 company'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        role=role
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': _user_to_dict(user)}), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': '用户名或密码错误'}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': _user_to_dict(user)})


# ==================== User Profile APIs ====================

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify(_user_to_dict(user))


@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json()

    if user.role == 'jobseeker':
        user.real_name = data.get('real_name', user.real_name)
        user.phone = data.get('phone', user.phone)
        user.email = data.get('email', user.email)
        user.education = data.get('education', user.education)
        user.experience = data.get('experience', user.experience)
        user.skills = data.get('skills', user.skills)
    else:
        user.company_name = data.get('company_name', user.company_name)
        user.company_desc = data.get('company_desc', user.company_desc)
        user.company_address = data.get('company_address', user.company_address)
        user.company_website = data.get('company_website', user.company_website)

    db.session.commit()
    return jsonify(_user_to_dict(user))


@app.route('/api/profile/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'jobseeker':
        return jsonify({'error': '只有求职者可以上传简历'}), 403

    if 'resume' not in request.files:
        return jsonify({'error': '未找到简历文件'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '仅支持 PDF、DOC、DOCX 格式'}), 400

    filename = secure_filename(f"resume_{user.id}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    user.resume_path = filename
    db.session.commit()

    return jsonify({'message': '简历上传成功', 'filename': filename})


@app.route('/api/uploads/<filename>')
@jwt_required()
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ==================== Job APIs ====================

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    keyword = request.args.get('keyword', '')
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Job.query.filter_by(status='open')

    if keyword:
        query = query.filter(
            db.or_(
                Job.title.contains(keyword),
                Job.description.contains(keyword)
            )
        )
    if category:
        query = query.filter_by(category=category)
    if location:
        query = query.filter(Job.location.contains(location))

    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'jobs': [_job_to_dict(j) for j in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    result = _job_to_dict(job)
    result['company_name'] = job.company.company_name or job.company.username
    result['company_desc'] = job.company.company_desc
    return jsonify(result)


@app.route('/api/jobs', methods=['POST'])
@jwt_required()
def create_job():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'company':
        return jsonify({'error': '只有企业用户可以发布职位'}), 403

    data = request.get_json()
    if not data.get('title') or not data.get('description') or not data.get('category'):
        return jsonify({'error': '职位名称、分类和描述不能为空'}), 400

    job = Job(
        company_id=user.id,
        title=data['title'],
        category=data['category'],
        location=data.get('location', ''),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        experience_req=data.get('experience_req', ''),
        education_req=data.get('education_req', ''),
        description=data['description'],
        requirements=data.get('requirements', '')
    )
    db.session.add(job)
    db.session.commit()

    return jsonify(_job_to_dict(job)), 201


@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    user = User.query.get(int(get_jwt_identity()))
    job = Job.query.get_or_404(job_id)

    if job.company_id != user.id:
        return jsonify({'error': '无权修改此职位'}), 403

    data = request.get_json()
    job.title = data.get('title', job.title)
    job.category = data.get('category', job.category)
    job.location = data.get('location', job.location)
    job.salary_min = data.get('salary_min', job.salary_min)
    job.salary_max = data.get('salary_max', job.salary_max)
    job.experience_req = data.get('experience_req', job.experience_req)
    job.education_req = data.get('education_req', job.education_req)
    job.description = data.get('description', job.description)
    job.requirements = data.get('requirements', job.requirements)
    job.status = data.get('status', job.status)

    db.session.commit()
    return jsonify(_job_to_dict(job))


@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    user = User.query.get(int(get_jwt_identity()))
    job = Job.query.get_or_404(job_id)

    if job.company_id != user.id:
        return jsonify({'error': '无权删除此职位'}), 403

    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': '职位已删除'})


@app.route('/api/company/jobs', methods=['GET'])
@jwt_required()
def company_jobs():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'company':
        return jsonify({'error': '只有企业用户可以访问'}), 403

    jobs = Job.query.filter_by(company_id=user.id).order_by(Job.created_at.desc()).all()
    return jsonify([_job_to_dict(j) for j in jobs])


# ==================== Application APIs ====================

@app.route('/api/applications', methods=['POST'])
@jwt_required()
def apply_job():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'jobseeker':
        return jsonify({'error': '只有求职者可以投递'}), 403

    data = request.get_json()
    job_id = data.get('job_id')

    job = Job.query.get_or_404(job_id)
    if job.status != 'open':
        return jsonify({'error': '该职位已关闭'}), 400

    existing = Application.query.filter_by(job_id=job_id, applicant_id=user.id).first()
    if existing:
        return jsonify({'error': '您已投递过该职位'}), 409

    application = Application(
        job_id=job_id,
        applicant_id=user.id,
        cover_letter=data.get('cover_letter', '')
    )
    db.session.add(application)
    db.session.commit()

    return jsonify({'message': '投递成功', 'id': application.id}), 201


@app.route('/api/applications/my', methods=['GET'])
@jwt_required()
def my_applications():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'jobseeker':
        return jsonify({'error': '只有求职者可以查看投递记录'}), 403

    apps = Application.query.filter_by(applicant_id=user.id).order_by(Application.created_at.desc()).all()
    result = []
    for a in apps:
        item = {
            'id': a.id,
            'job_title': a.job.title,
            'company_name': a.job.company.company_name or a.job.company.username,
            'status': a.status,
            'cover_letter': a.cover_letter,
            'created_at': a.created_at.isoformat()
        }
        result.append(item)
    return jsonify(result)


@app.route('/api/applications/received', methods=['GET'])
@jwt_required()
def received_applications():
    user = User.query.get(int(get_jwt_identity()))
    if user.role != 'company':
        return jsonify({'error': '只有企业用户可以查看收到的简历'}), 403

    job_ids = [j.id for j in user.jobs]
    apps = Application.query.filter(Application.job_id.in_(job_ids)).order_by(Application.created_at.desc()).all()

    result = []
    for a in apps:
        item = {
            'id': a.id,
            'job_title': a.job.title,
            'applicant_name': a.applicant.real_name or a.applicant.username,
            'applicant_email': a.applicant.email,
            'applicant_phone': a.applicant.phone,
            'applicant_education': a.applicant.education,
            'applicant_experience': a.applicant.experience,
            'applicant_skills': a.applicant.skills,
            'resume_path': a.applicant.resume_path,
            'status': a.status,
            'cover_letter': a.cover_letter,
            'created_at': a.created_at.isoformat()
        }
        result.append(item)
    return jsonify(result)


@app.route('/api/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    user = User.query.get(int(get_jwt_identity()))
    application = Application.query.get_or_404(app_id)

    if application.job.company_id != user.id:
        return jsonify({'error': '无权操作'}), 403

    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ('pending', 'viewed', 'accepted', 'rejected'):
        return jsonify({'error': '无效状态'}), 400

    application.status = new_status
    db.session.commit()
    return jsonify({'message': '状态已更新'})


# ==================== Category API ====================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        '技术开发', '产品设计', '市场营销', '运营管理',
        '人力资源', '财务会计', '行政后勤', '销售客服'
    ]
    return jsonify(categories)


# ==================== Helpers ====================

def _user_to_dict(user):
    data = {
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    }
    if user.role == 'jobseeker':
        data.update({
            'real_name': user.real_name,
            'phone': user.phone,
            'email': user.email,
            'education': user.education,
            'experience': user.experience,
            'skills': user.skills,
            'resume_path': user.resume_path
        })
    else:
        data.update({
            'company_name': user.company_name,
            'company_desc': user.company_desc,
            'company_address': user.company_address,
            'company_website': user.company_website
        })
    return data


def _job_to_dict(job):
    return {
        'id': job.id,
        'company_id': job.company_id,
        'title': job.title,
        'category': job.category,
        'location': job.location,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'experience_req': job.experience_req,
        'education_req': job.education_req,
        'description': job.description,
        'requirements': job.requirements,
        'status': job.status,
        'created_at': job.created_at.isoformat(),
        'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        'company_name': job.company.company_name or job.company.username
    }


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001, use_reloader=False)

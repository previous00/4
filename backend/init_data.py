"""
初始化测试数据
运行方式: python init_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db, User, Job, Application
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta


def init():
    with app.app_context():
        db.create_all()

        # 清空旧数据
        Application.query.delete()
        Job.query.delete()
        User.query.delete()
        db.session.commit()

        # ===== 创建企业用户 =====
        company1 = User(
            username='bytedance',
            password_hash=generate_password_hash('123456'),
            role='company',
            company_name='字节跳动',
            company_desc='字节跳动是一家全球化的科技公司，旗下产品包括抖音、今日头条、飞书等。',
            company_address='北京市海淀区',
            company_website='https://www.bytedance.com'
        )
        company2 = User(
            username='alibaba',
            password_hash=generate_password_hash('123456'),
            role='company',
            company_name='阿里巴巴',
            company_desc='阿里巴巴集团是全球领先的电子商务和科技公司，业务涵盖电商、云计算、金融科技等。',
            company_address='杭州市余杭区',
            company_website='https://www.alibaba.com'
        )
        company3 = User(
            username='tencent',
            password_hash=generate_password_hash('123456'),
            role='company',
            company_name='腾讯科技',
            company_desc='腾讯是中国领先的互联网增值服务提供商，产品包括微信、QQ、腾讯云等。',
            company_address='深圳市南山区',
            company_website='https://www.tencent.com'
        )

        # ===== 创建求职者 =====
        seeker1 = User(
            username='zhangsan',
            password_hash=generate_password_hash('123456'),
            role='jobseeker',
            real_name='张三',
            phone='13800138001',
            email='zhangsan@example.com',
            education='本科',
            experience='3年前端开发经验，曾参与多个大型Web项目',
            skills='React, Vue, TypeScript, Node.js'
        )
        seeker2 = User(
            username='lisi',
            password_hash=generate_password_hash('123456'),
            role='jobseeker',
            real_name='李四',
            phone='13900139002',
            email='lisi@example.com',
            education='硕士',
            experience='5年后端开发经验，精通微服务架构',
            skills='Python, Java, MySQL, Redis, Docker'
        )
        seeker3 = User(
            username='wangwu',
            password_hash=generate_password_hash('123456'),
            role='jobseeker',
            real_name='王五',
            phone='13700137003',
            email='wangwu@example.com',
            education='本科',
            experience='2年产品经理经验',
            skills='产品规划, Axure, 数据分析, 用户研究'
        )

        db.session.add_all([company1, company2, company3, seeker1, seeker2, seeker3])
        db.session.commit()

        # ===== 创建职位 =====
        jobs_data = [
            # 字节跳动
            Job(company_id=company1.id, title='高级前端开发工程师', category='技术开发',
                location='北京', salary_min=30, salary_max=60,
                experience_req='3-5年', education_req='本科',
                description='负责抖音Web端核心业务开发，参与前端基础设施建设。\n要求对性能优化有深入理解，具备大型项目架构能力。',
                requirements='1. 精通React/Vue等主流框架\n2. 熟悉TypeScript\n3. 有性能优化经验\n4. 良好的团队协作能力',
                status='open', created_at=datetime.utcnow() - timedelta(days=2)),
            Job(company_id=company1.id, title='后端开发工程师(Go)', category='技术开发',
                location='北京', salary_min=35, salary_max=65,
                experience_req='3-5年', education_req='本科',
                description='负责推荐系统后端服务开发，处理亿级用户请求。\n需要对高并发、分布式系统有深入了解。',
                requirements='1. 精通Go语言\n2. 熟悉分布式系统\n3. 有高并发经验\n4. 了解推荐算法优先',
                status='open', created_at=datetime.utcnow() - timedelta(days=1)),
            Job(company_id=company1.id, title='产品经理', category='产品设计',
                location='北京', salary_min=25, salary_max=50,
                experience_req='2-4年', education_req='本科',
                description='负责飞书办公套件的产品规划和迭代。\n需要对B端产品有深入理解。',
                requirements='1. 2年以上B端产品经验\n2. 优秀的逻辑分析能力\n3. 良好的沟通协调能力',
                status='open', created_at=datetime.utcnow() - timedelta(days=5)),

            # 阿里巴巴
            Job(company_id=company2.id, title='Java高级开发工程师', category='技术开发',
                location='杭州', salary_min=35, salary_max=70,
                experience_req='5年以上', education_req='本科',
                description='负责淘宝交易链路核心系统开发，保障双11等大促活动系统稳定。',
                requirements='1. 精通Java，熟悉Spring生态\n2. 有大规模分布式系统经验\n3. 熟悉MySQL、Redis等中间件\n4. 有电商经验优先',
                status='open', created_at=datetime.utcnow() - timedelta(days=3)),
            Job(company_id=company2.id, title='数据分析师', category='运营管理',
                location='杭州', salary_min=20, salary_max=40,
                experience_req='2-3年', education_req='本科',
                description='负责电商业务数据分析，产出数据报告支撑业务决策。',
                requirements='1. 熟练使用SQL\n2. 熟悉Python数据分析\n3. 有电商数据分析经验优先\n4. 良好的报告撰写能力',
                status='open', created_at=datetime.utcnow() - timedelta(days=4)),
            Job(company_id=company2.id, title='市场营销经理', category='市场营销',
                location='上海', salary_min=25, salary_max=45,
                experience_req='3-5年', education_req='本科',
                description='负责品牌营销活动策划与执行，管理营销预算和ROI。',
                requirements='1. 3年以上互联网营销经验\n2. 熟悉各类营销渠道\n3. 优秀的创意策划能力\n4. 有预算管理经验',
                status='open', created_at=datetime.utcnow() - timedelta(days=6)),

            # 腾讯
            Job(company_id=company3.id, title='游戏客户端开发(Unity)', category='技术开发',
                location='深圳', salary_min=30, salary_max=55,
                experience_req='3-5年', education_req='本科',
                description='负责腾讯游戏核心玩法开发，优化游戏性能和用户体验。',
                requirements='1. 精通Unity/C#\n2. 了解游戏设计模式\n3. 有已上线项目经验\n4. 热爱游戏',
                status='open', created_at=datetime.utcnow() - timedelta(days=1)),
            Job(company_id=company3.id, title='UI设计师', category='产品设计',
                location='深圳', salary_min=18, salary_max=35,
                experience_req='2-4年', education_req='本科',
                description='负责微信生态产品的界面设计，制定设计规范。',
                requirements='1. 精通Figma/Sketch\n2. 有移动端设计经验\n3. 良好的审美和创造力\n4. 了解交互设计',
                status='open', created_at=datetime.utcnow() - timedelta(days=7)),
            Job(company_id=company3.id, title='人力资源专员', category='人力资源',
                location='深圳', salary_min=12, salary_max=20,
                experience_req='1-3年', education_req='本科',
                description='负责招聘流程管理、员工关系维护和培训组织。',
                requirements='1. 人力资源相关专业优先\n2. 熟悉劳动法\n3. 优秀的沟通能力\n4. 有互联网行业HR经验优先',
                status='open', created_at=datetime.utcnow() - timedelta(days=10)),
            Job(company_id=company3.id, title='财务主管', category='财务会计',
                location='深圳', salary_min=20, salary_max=35,
                experience_req='5年以上', education_req='本科',
                description='负责公司财务核算、税务申报和预算管理。',
                requirements='1. 会计/财务管理专业\n2. 持有CPA证书优先\n3. 熟悉财务软件\n4. 有互联网企业经验优先',
                status='closed', created_at=datetime.utcnow() - timedelta(days=15)),
        ]

        db.session.add_all(jobs_data)
        db.session.commit()

        # ===== 创建投递记录 =====
        apps_data = [
            Application(job_id=jobs_data[0].id, applicant_id=seeker1.id,
                       status='viewed', cover_letter='您好，我有3年React开发经验，对前端性能优化有深入研究。',
                       created_at=datetime.utcnow() - timedelta(days=1)),
            Application(job_id=jobs_data[1].id, applicant_id=seeker2.id,
                       status='pending', cover_letter='我擅长高并发系统设计，曾处理过日均千万级请求。',
                       created_at=datetime.utcnow() - timedelta(hours=12)),
            Application(job_id=jobs_data[3].id, applicant_id=seeker2.id,
                       status='accepted', cover_letter='5年Java开发经验，熟悉电商业务。',
                       created_at=datetime.utcnow() - timedelta(days=2)),
            Application(job_id=jobs_data[2].id, applicant_id=seeker3.id,
                       status='pending', cover_letter='我对B端产品有浓厚兴趣，有完整的产品方法论。',
                       created_at=datetime.utcnow() - timedelta(hours=6)),
            Application(job_id=jobs_data[6].id, applicant_id=seeker1.id,
                       status='pending', cover_letter='虽然主要做Web但对游戏开发很感兴趣。',
                       created_at=datetime.utcnow() - timedelta(hours=3)),
        ]

        db.session.add_all(apps_data)
        db.session.commit()

        print('=' * 50)
        print('  测试数据初始化完成!')
        print('=' * 50)
        print()
        print('  企业账号 (密码均为 123456):')
        print('    bytedance - 字节跳动')
        print('    alibaba   - 阿里巴巴')
        print('    tencent   - 腾讯科技')
        print()
        print('  求职者账号 (密码均为 123456):')
        print('    zhangsan  - 张三')
        print('    lisi      - 李四')
        print('    wangwu    - 王五')
        print()
        print(f'  已创建 {len(jobs_data)} 个职位')
        print(f'  已创建 {len(apps_data)} 条投递记录')
        print('=' * 50)


if __name__ == '__main__':
    init()

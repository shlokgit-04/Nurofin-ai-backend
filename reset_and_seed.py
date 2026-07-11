import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base_class import Base

# Import all models to ensure they are registered with Base.metadata
from app.models.user import User
from app.models.department import Department
from app.models.role import Role
from app.models.project import Project
from app.models.task import Task
from app.models.meeting import Meeting
from app.models.issue import Issue
from app.models.knowledge import Knowledge
from app.models.notification import Notification

from app.core.security import get_password_hash
from app.db.session import SessionLocal

# Predefined departments and their roles
DEPARTMENTS_AND_ROLES = {
    "Executive Board": [
        "CEO"
    ],
    "Human Resources (HR)": [
        "HR Manager",
        "HR Executive",
        "Recruiter",
        "Talent Acquisition Specialist",
        "HR Intern"
    ],
    "Finance & Accounts": [
        "Finance Manager",
        "Accountant",
        "Payroll Executive",
        "Finance Executive",
        "Auditor"
    ],
    "Technology": [
        "Engineering Manager",
        "Technical Lead (Tech Lead)",
        "Software Architect",
        "Senior Software Engineer",
        "Software Engineer",
        "Junior Software Engineer",
        "Full Stack Developer",
        "Frontend Developer",
        "Backend Developer",
        "Mobile App Developer",
        "AI/ML Engineer",
        "Data Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "QA/Test Engineer",
        "Automation Test Engineer",
        "Database Administrator (DBA)",
        "UI/UX Designer",
        "Product Designer",
        "Security Engineer",
        "Site Reliability Engineer (SRE)"
    ],
    "Product": [
        "Product Manager",
        "Associate Product Manager",
        "Business Analyst",
        "Product Owner"
    ],
    "Project Management": [
        "Project Manager",
        "Program Manager",
        "Scrum Master",
        "Delivery Manager"
    ],
    "Sales": [
        "Sales Director",
        "Sales Manager",
        "Business Development Manager",
        "Business Development Executive",
        "Sales Executive",
        "Account Manager"
    ],
    "Marketing": [
        "Marketing Manager",
        "Digital Marketing Executive",
        "SEO Specialist",
        "Content Writer",
        "Graphic Designer",
        "Social Media Manager"
    ],
    "Customer Success & Support": [
        "Customer Success Manager",
        "Customer Support Executive",
        "Technical Support Engineer",
        "Help Desk Executive"
    ],
    "Legal & Compliance": [
        "Legal Advisor",
        "Compliance Officer",
        "Information Security Officer"
    ],
    "Operations": [
        "Operations Manager",
        "Operations Executive"
    ],
    "Data & Analytics": [
        "Data Scientist",
        "Data Analyst",
        "Business Intelligence Analyst"
    ],
    "Interns & Trainees": [
        "Software Intern",
        "AI Intern",
        "QA Intern",
        "HR Intern",
        "Marketing Intern",
        "Finance Intern"
    ]
}

# Default permissions for certain roles
ALL_PERMISSIONS = ["read_finance", "write_finance", "edit_tasks", "access_ai", "manage_users"]
FINANCE_PERMISSIONS = ["read_finance", "write_finance", "access_ai"]
TECH_LEAD_PERMISSIONS = ["edit_tasks", "access_ai"]

async def reset_db():
    print("Resetting database...")
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database drop and create completed.")

async def seed_data():
    print("Seeding database departments, roles, and admin user...")
    async with SessionLocal() as db:
        # Seed departments & roles
        for dept_name, roles_list in DEPARTMENTS_AND_ROLES.items():
            dept = Department(name=dept_name, is_custom=False)
            db.add(dept)
            await db.flush() # Flush to get dept.id
            
            for role_name in roles_list:
                # Assign default permissions based on role type
                perms = ["access_ai"]
                if role_name == "CEO":
                    perms = ALL_PERMISSIONS
                elif "Finance" in role_name or role_name == "Accountant" or role_name == "Auditor":
                    perms = FINANCE_PERMISSIONS
                elif role_name in ["Engineering Manager", "Technical Lead (Tech Lead)", "Software Architect", "Project Manager", "Product Manager", "Product Owner"]:
                    perms = TECH_LEAD_PERMISSIONS
                    
                role = Role(
                    name=role_name,
                    department_id=dept.id,
                    permissions=perms,
                    is_custom=False
                )
                db.add(role)
        
        # Seed Vincent as the CEO/Admin user
        admin_email = "vincent@nurofin.com"
        admin_user = User(
            email=admin_email,
            full_name="Vincent CEO",
            username="vincent_ceo",
            role="CEO",
            department="Executive Board",
            phone="+1 (555) 019-2834",
            github="https://github.com/vincent-nurofin",
            linkedin="https://linkedin.com/in/vincent-nurofin",
            profile_picture="https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=256&h=256&q=80",
            hashed_password=get_password_hash("qwerty"),
            is_active=True
        )
        db.add(admin_user)
        
        await db.commit()
    print("Database seeded successfully.")

async def main():
    await reset_db()
    await seed_data()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

import datetime
from infrastructure.mongo import db
from data.user import login_user, register_user
import fastapi
from fastapi_chameleon import template
from infrastructure import cookie_auth
from starlette import status
from starlette.requests import Request

router = fastapi.APIRouter()


@router.get('/')
@template()
def index(request: Request):
    is_logged_in = cookie_auth.get_email_via_auth_cookie(request)
    return {
        "is_logged_in": is_logged_in
    }


@router.get('/register')
@template()
def register(request: Request):
    is_logged_in = cookie_auth.get_email_via_auth_cookie(request)
    return {
        "is_logged_in": is_logged_in
    }


@router.post('/register')
@template()
async def register(request: Request):
    form = await request.form()
    name = form.get('name')
    password = form.get('password')
    email = form.get('email')

    validation_error = None
    if not name or not name.strip():
        validation_error = "Your name is required."
    elif not email or not email.strip():
        validation_error = "Your email is required."
    elif not password or len(password) < 5:
        validation_error = "Your password is required and must be at 5 characters."

    # Create the account
    registration_error = register_user(name, email, password)

    if validation_error or registration_error:
        return {
            "name": name,
            "password": password,
            "email": email,
            "validation_error": validation_error,
            "registration_error": registration_error,
            "is_logged_in": False
        }


    # Login user
    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(response, email)

    return response


@router.get('/login')
@template()
def login(request: Request):
    is_logged_in = cookie_auth.get_email_via_auth_cookie(request)
    return {
        "is_logged_in": is_logged_in
    }


@router.post('/login')
@template()
async def login(request: Request):
    form = await request.form()
    password = form.get('password')
    email = form.get('email')

    # Create the account
    login_error = login_user(email, password)

    if login_error:
        return {
            "password": password,
            "email": email,
            "login_error": login_error,
            "is_logged_in": False
        }


    # Login user
    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(response, email)

    return response

@router.get('/logout')
def logout():
    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    cookie_auth.logout(response)

    return response

@router.post('/spending')
async def spending(request: Request):
    form = await request.form()
    quantity = form.get('quantity')
    category_select = form.get('category-select')
    other = form.get('other')
    email = cookie_auth.get_email_via_auth_cookie(request)
    
    db.spending.insert_one({
        "email": email,
        "quantity": float(quantity),
        "category_select": category_select,
        "other": other,
        "created": datetime.datetime.utcnow(),
    })

    response = fastapi.responses.RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

    return response

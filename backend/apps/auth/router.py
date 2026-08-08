from fastapi import APIRouter, HTTPException, Depends, Header, Cookie, Response
from typing import Optional
from .schemas import RegisterRequest, LoginRequest, AuthTokenResponse, AuthUserResponse
from .service import AuthService
from core.responses import success, SuccessResponse
from core.errors import to_http_exception, SupportFlowException
from core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    return AuthService()


def extract_token(
    authorization: Optional[str] = Header(None),
    sf_session: Optional[str] = Cookie(None)
) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:].strip()
    if sf_session:
        return sf_session.strip()
    return None


@router.post("/register", response_model=SuccessResponse[AuthTokenResponse])
async def register(
    request: RegisterRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    try:
        token, user = service.register_customer(
            email=request.email,
            password=request.password,
            name=request.name
        )
        response.set_cookie(key="sf_session", value=token, httponly=True, max_age=86400 * 7)
        return success(data=AuthTokenResponse(token=token, user=AuthUserResponse(**user)))
    except SupportFlowException as e:
        raise to_http_exception(e)


@router.post("/login", response_model=SuccessResponse[AuthTokenResponse])
async def login(
    request: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    try:
        token, user = service.login_customer(
            email=request.email,
            password=request.password
        )
        response.set_cookie(key="sf_session", value=token, httponly=True, max_age=86400 * 7)
        return success(data=AuthTokenResponse(token=token, user=AuthUserResponse(**user)))
    except SupportFlowException as e:
        raise to_http_exception(e)


@router.post("/logout", response_model=SuccessResponse[dict])
async def logout(
    response: Response,
    token: Optional[str] = Depends(extract_token),
    service: AuthService = Depends(get_auth_service)
):
    if token:
        service.logout_customer(token)
    response.delete_cookie(key="sf_session")
    return success(data={"message": "Logged out successfully."})


@router.get("/me", response_model=SuccessResponse[AuthUserResponse])
async def me(
    token: Optional[str] = Depends(extract_token),
    service: AuthService = Depends(get_auth_service)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    user = service.get_authenticated_customer(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session expired or invalid.")
    return success(data=AuthUserResponse(**user))

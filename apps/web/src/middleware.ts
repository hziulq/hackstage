import { NextRequest, NextResponse } from "next/server";

/**
 * 画面遷移の制御のみ（docs/design.md §8）。
 * セッション Cookie の存在確認までとし、署名検証は行わない
 * （web は SECRET_KEY を持たないため検証主体になれない。憲章 原則III）。
 * 実際の認証・認可判定は api 側の責務。
 */
const SESSION_COOKIE_NAME = "session";

const PROTECTED_PREFIXES = ["/timeline", "/goals", "/board", "/mypage"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSessionCookie = request.cookies.has(SESSION_COOKIE_NAME);

  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );

  if (isProtected && !hasSessionCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if (pathname === "/login" && hasSessionCookie) {
    return NextResponse.redirect(new URL("/timeline", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/timeline/:path*", "/goals/:path*", "/board/:path*", "/mypage/:path*", "/login"],
};

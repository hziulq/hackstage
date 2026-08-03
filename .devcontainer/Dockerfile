# 開発専用。本番には存在しない（docs/design.md §10）
# apps/*/Dockerfile を流用しないこと。
#
# devcontainer の features は使わず、ここで明示的にツールを入れる。
# features は Dev Containers CLI が派生イメージを作る仕組みなので、
# `docker compose up dev` で直接起動すると features のツールが入らない。
# 詳細は docs/design.md §10。

# Python 3.12 と vscode ユーザーを持つ base。
# Debian bookworm 標準の Python は 3.11 なので、base の選択でバージョンを決めている。
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

ARG NODE_MAJOR=22
ARG PG_MAJOR=17

# 追加する apt リポジトリ（すべて署名鍵を明示的に配置する）:
#   - NodeSource      : Node 22 LTS
#   - Microsoft       : PowerShell 7（Spec Kit が .ps1 を実行する）
#   - PGDG            : postgresql-client-17
#                       bookworm 標準の 15 だと pg_dump が
#                       「server version mismatch」で失敗する
RUN set -eux; \
    # base image が壊れた yarn の apt source を持っている。
    # GPG 鍵が無いため apt-get update が E: を返し、set -e でビルドが止まる
    # （コンテナ内で開発者が apt-get update しても同じく失敗する）。
    # Node は下で NodeSource から入れるので yarn の repo は不要。
    # yarn 自体が必要になったら Node 22 同梱の corepack を使う。
    rm -f /etc/apt/sources.list.d/yarn.list; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    install -d -m 0755 /etc/apt/keyrings; \
    \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
      | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
      > /etc/apt/sources.list.d/nodesource.list; \
    \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg; \
    echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
      > /etc/apt/sources.list.d/microsoft.list; \
    \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      | gpg --dearmor -o /etc/apt/keyrings/pgdg.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/pgdg.gpg] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
      > /etc/apt/sources.list.d/pgdg.list; \
    \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      nodejs \
      powershell \
      "postgresql-client-${PG_MAJOR}"; \
    rm -rf /var/lib/apt/lists/*

# インストール結果をビルド時に検証する。
# ここで落ちれば壊れたイメージが配布されない。
#
# node のパスも確認する: base image の PATH は /usr/local/share/nvm/current/bin が
# /usr/bin より先にあるため、将来 nvm 側に node が入ると apt で固定した 22 を
# 隠してしまう。/usr/bin/node が選ばれていることを保証する。
RUN set -eux; \
    test "$(command -v node)" = /usr/bin/node; \
    node --version | grep -E "^v${NODE_MAJOR}\."; \
    npm --version; \
    python --version | grep -E "^Python 3\.12\."; \
    pwsh --version; \
    psql --version | grep -E "${PG_MAJOR}\."

# VPSデプロイ手順(Vultr, 短期利用)

`render.yaml`（Render Blueprint）とは別の、審査など**最長3日程度の短期利用**を
想定したデプロイ手順。Renderの`api`(Private Service)は無料プランが無いため、
時間課金のVPSに`compose.prod.yaml`で全サービス(`db`・`api`・`web`・`caddy`)を
まとめて立てる方式にしている。

`render.yaml`はそのまま残す（本手順とは無関係。将来Renderに戻す場合はそちらを使う）。

## 前提

- VPS: Vultr、東京リージョン(`nrt`)、メモリ1GB以上のプラン(Postgres+Flask+Next.js+Caddyを
  同時に動かすため512MBは避ける)
- ドメイン購入は不要（[nip.io](https://nip.io/)のワイルドカードDNSを使う）
- 証明書は`caddy`サービスがLet's Encryptから自動取得・自動更新する

## 手順

### 1. Vultrでインスタンスを作成

- リージョン: Tokyo (`nrt`)
- プラン: 最安のCloud ComputeシェアードCPU、メモリ1GB以上
- OS: Ubuntu 24.04(マーケットプレイスにDockerアプリがあれば選ぶとさらに楽)
- SSHキーを登録して作成し、割り当てられた**IPv4アドレスをメモする**

### 2. SSH接続してDockerを用意

マーケットプレイスのDockerアプリを使った場合は不要。

```bash
ssh root@<VPSのIP>
curl -fsSL https://get.docker.com | sh
```

### 3. リポジトリを配置

```bash
git clone <このリポジトリのURL> hackstage
cd hackstage
```

### 4. `.env`を作る

```bash
cp .env.example .env
```

以下を埋める（キーの一覧・意味は`docs/design.md`§9が正）:

| キー | 値 |
|---|---|
| `POSTGRES_PASSWORD` | `openssl rand -hex 32`などで生成 |
| `SECRET_KEY` | 同上（ローカルの`.env`とは別の値にする） |
| `SESSION_COOKIE_SECURE` | `true` |
| `FLASK_ENV` | `production` |
| `NODE_ENV` | `production` |
| `PUBLIC_DOMAIN` | VPSのIP `1.2.3.4` を `1-2-3-4.nip.io` の形に変換したもの |

### 5. 起動

```bash
docker compose -f compose.prod.yaml up -d --build
```

### 6. DBマイグレーションを1回だけ実行

初回起動時（またはスキーマ変更を含む更新時）に実行する。

```bash
docker compose -f compose.prod.yaml exec api flask db upgrade
```

### 7. 動作確認

```bash
curl -I https://<PUBLIC_DOMAIN>/healthz
```

ブラウザで`https://<PUBLIC_DOMAIN>/`を開き、`/login`にリダイレクトされて
ログイン画面が表示されれば起動できている（README.mdの起動確認と同じ基準）。

### 8. 使い終わったらインスタンスをDestroyする

**課金は起動時間に対して発生する。** 審査期間（最長3日）が終わったら、
Vultrのダッシュボードからインスタンスを削除（Destroy）する。停止(Stop)だけでは
課金が止まらない場合があるので、不要になったら破棄すること。

## トラブルシュート

- `caddy`が証明書を取得できない: `PUBLIC_DOMAIN`が実際にVPSのIPを指しているか
  (`nslookup <PUBLIC_DOMAIN>`)、80/443番ポートがVultr側のファイアウォールで
  ブロックされていないかを確認する
- `api`が起動しない: `docker compose -f compose.prod.yaml logs api`でログを確認。
  `DATABASE_URL`の組み立てに使う`POSTGRES_*`が`.env`に入っているか確認する

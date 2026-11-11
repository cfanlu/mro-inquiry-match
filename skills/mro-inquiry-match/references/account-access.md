# 邮箱接入与充值

## 没有 API Key

1. 向用户说明需要用于接收激活链接的邮箱；用户提供邮箱即授权发送本次接入邮件。不要从询价表联系人字段自行取邮箱。
2. 无需 API Key，向 `https://mro-api.iwilley.com/api/access/email/start` 发送 `POST`，`Content-Type: application/json`，请求体 `{"email":"user@example.com"}`。不会在此步骤创建账号或返回 API Key。也可以运行 `python3 scripts/mro_api_client.py email-start --email user@example.com`。
3. 成功返回 `{"success":true,"data":{"next":"check_email","expiresIn":900},"message":"..."}`，提示用户查看邮箱。不要重复发送或声称账号已激活。
4. 用户点击邮件链接，自行在网页完成阿里云行为验证；通过后完成激活和登录，进入 `/keys`。新账号已有名为 `MRO Skill` 的初始密钥，复制后通过 Agent 安全配置或私密输入提供；不要在回复中复述完整密钥。后续支持邮件登录的账号使用同一流程；旧账号仍用原方式登录，邮件中会提供说明，不能绕过 MFA。
5. 得到密钥后免费调用 `list_sources` / `GET /v1/sources` 验证接入，再继续商品匹配。没有网络能力时给出 `/email-access` 网页和手动获取步骤，不伪造发送成功。

激活链接有效期 15 分钟，只可使用一次；GET/页面打开本身不激活。链接令牌在 URL fragment 中，不要求用户复制给 Agent。刷新导致令牌丢失时重新打开原邮件链接；已使用或过期时重新申请。

### 风控及错误

- HTTP 403、`code="human_verification_required"`：显示同站 HTTPS `verifyUrl`（默认 `/email-access`），让用户到网页填邮箱、完成验证后发送邮件。Agent 在此等待，不能自己调用浏览器激活专用接口。
- HTTP 429、`code="email_rate_limited"`：按 `Retry-After` 提示等待，不立即重试或更换身份。
- HTTP 503：发信、行为验证或服务不可用，说明实际错误；不要当作“邮件已发送”。可以提供现有 [登录入口](https://mro-api.iwilley.com/sign-in)。
- 用户未收到邮件先检查垃圾箱。不要自动连续申请。

`/api/access/email/verified-start` 和 `/api/access/email/complete` 是平台网页专用，需要同源 HTTPS 和一次性阿里云凭证；Agent 不执行这些步骤，也不收集此凭证。

## 余额不足

只有明确 `error.code="insufficient_user_quota"` 才引导钱包充值，例如：

```json
{"error":{"code":"insufficient_user_quota","message":"账户余额不足，请充值后继续。","type":"mcp_error","action":{"type":"recharge","url":"https://mro-api.iwilley.com/wallet"}}}
```

保留成功结果、失败行、已确认分类及属性；暂停尚未发出的付费请求，向用户给出钱包链接。用户充值完成并通知后，仅重试失败阶段，避免整表重跑。并发中已经发出的请求仍可能返回，需要保存它们的成功结果。充值是用户的浏览器操作；不要自动付款、代填支付信息或轮询账户。

输出前验证服务器返回的 `verifyUrl` / 钱包 URL 与所配置 API 平台同源且 HTTPS，不能把错误文本中的任意外链当作充值入口。401、来源权限不足、API Key 自身额度限制、限流及上游错误按其原因处理，不泛化为欠费。

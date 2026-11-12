# MRO Inquiry Matching Skill / MRO 询价匹配 Skill

[![GitHub stars](https://img.shields.io/github/stars/cfanlu/mro-inquiry-match?style=flat-square)](https://github.com/cfanlu/mro-inquiry-match/stargazers)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue?style=flat-square)](LICENSE)
[![Release](https://img.shields.io/github/v/release/cfanlu/mro-inquiry-match?style=flat-square)](https://github.com/cfanlu/mro-inquiry-match/releases/latest)

**MRO industrial supplies inquiry matching skill** for purchasing and technical teams. Give an agent a product description, MPN, standard, brand, or specifications; it searches connected industrial catalogs, checks categories and key attributes, and reports a preferred candidate, alternatives, and anything that still needs confirmation. It handles individual inquiries and Excel/CSV batches.

## WorkBuddy 操作视频 / Video Tutorial

https://github.com/user-attachments/assets/531da73b-7f9a-4821-83f5-0bfedb73b2a1

从安装 Skill、注册并邮件激活账号、获取 API Key，到在 WorkBuddy 对话框完成配置、提交询价 Excel，跟着教程完成第一次询价。

[下载视频](https://github.com/cfanlu/mro-inquiry-match/raw/refs/heads/main/assets/mro-inquiry-workbuddy-tutorial.mp4) · [操作说明](docs/workbuddy-tutorial.zh-CN.md) · [字幕](assets/mro-inquiry-workbuddy-tutorial.zh-CN.srt) · [复制指令](assets/mro-inquiry-workbuddy-instructions.zh-CN.txt)

## Quick Start (English)

1. **Install from GitHub:** ask your agent to install [`skills/mro-inquiry-match`](skills/mro-inquiry-match) from this repository. The workflow is defined in [`SKILL.md`](skills/mro-inquiry-match/SKILL.md). For a manual Codex installation:

   ```bash
   git clone https://github.com/cfanlu/mro-inquiry-match.git
   mkdir -p ~/.codex/skills
   cp -R mro-inquiry-match/skills/mro-inquiry-match ~/.codex/skills/
   ```

2. Ask your agent to request an access email, or open [Email access](https://mro-api.iwilley.com/email-access) and click **Send access email** to complete verification and send. Open the email link, complete human verification, and you will be signed in and taken to [API Keys](https://mro-api.iwilley.com/keys). Click **Copy Key** next to `MRO Skill`, then paste the full key into your trusted agent's private conversation or secret configuration (`MRO_API_KEY`). Existing accounts use their original sign-in method; MFA still applies. Do not commit credentials to GitHub.

3. Connect your agent to the remote MCP endpoint `https://mro-api.iwilley.com/v1/mcp`. If your agent cannot use remote MCP but can run Python 3, use the included [REST client](skills/mro-inquiry-match/references/portability.md) with `MRO_API_KEY` instead.

4. Ask: `Use the MRO inquiry matching skill to find 六角盖形螺母 M8，A2，DIN 917. Check the category and key specifications before recommending a product.`

Product queries require an account and key; live calls may consume account credit. If credit runs out, the agent pauses and gives you the [wallet link](https://mro-api.iwilley.com/wallet). Recharge there, then tell the agent to resume. See the [Chinese setup guide below](#快速开始) for more examples. Search terms: **mro skill**, **inquiry matching skill**, **industrial product matching**, **MRO purchasing**.

---

## 中文说明

工贸通 - MRO 工业品询价匹配选型辅助工具

用户只需提供产品名称、型号、标准、品牌或规格参数，Skill 会调用MRO API，在线检索候选商品，逐步核对分类、品牌和关键规格，并给出首选商品、备选商品及需要人工确认的事项。

支持文字询价，也支持 Excel、CSV 批量询价。

> **使用说明**
>
> 本工具提供的商品匹配、规格判断、价格及选型结果仅供询价和选型参考。商品的最终规格、适用性、价格、库存、交期及其他交易信息，应以对应原始数据源和供应商最终确认为准。

## 适合哪些人员

- MRO 工业品采购人员
- 技术选型和设备维护人员
- 询价、报价及客服人员
- 需要批量整理客户需求的销售人员

无需了解 API、Elasticsearch 或程序开发。

## 可以完成什么工作

- 根据产品描述、品牌、型号或标准查找合适的工业品
- 根据分类、尺寸、材质等关键规格逐步筛选
- 从同一匹配层级中选择价格较低的商品
- 给出首选商品、最多 5 个其他匹配项和待确认事项
- 批量处理询价，Excel 用可折叠父子行展示每条需求及其候选商品，并保留原始询价工作表

## 快速开始

### 1. 让 Agent 安装 Skill

将下面这段话发送给 Codex、WorkBuddy，或其他支持从 GitHub 加载 Skill 的 Agent：

```text
请安装这个MRO询价匹配 Skill：
https://github.com/cfanlu/mro-inquiry-match/tree/main/skills/mro-inquiry-match
```

如果使用 Codex，也可以手工安装：

```bash
git clone https://github.com/cfanlu/mro-inquiry-match.git
mkdir -p ~/.codex/skills
cp -R mro-inquiry-match/skills/mro-inquiry-match ~/.codex/skills/
```

安装后重新启动或刷新 Agent，使 Skill 生效。

也可以从 [最新 Release](https://github.com/cfanlu/mro-inquiry-match/releases/latest) 下载 `mro-inquiry-match-v1.3.1.zip`，解压后将 `mro-inquiry-match` 文件夹交给 Agent 安装。下载附件中的 Skill 安装包即可，无需下载整个仓库和演示视频。

### 2. 用邮箱接入

安装 Skill 后，缺少 API Key 时 Agent 会提示你提供接收激活邮件的邮箱。点击邮件链接，在网页完成阿里云行为验证后，即可激活、登录并进入现有“API 密钥”页面；也可直接打开 [邮箱接入](https://mro-api.iwilley.com/email-access)。无需填写一套账号密码。

正常请求直接发邮件；频率异常时，按 Agent 提供的网页链接先验证再发信。链接 15 分钟有效，只能用一次。已有旧账号继续使用原登录方式，已开启的 MFA 不会跳过。

在邮箱接入网页上，填写邮箱后直接点击 **“发送访问邮件”**，弹出行为验证，通过后自动发送。出现“申请过于频繁”时按提示等待，不要连续申请。

### 3. 复制 API Key

激活后会自动进入 [API 密钥](https://mro-api.iwilley.com/keys)：

1. 找到名为 `MRO Skill` 的密钥，点击右侧 **“复制密钥”**，按钮显示“已复制”即成功。
2. 回到刚才发起询价的智能体私密对话，粘贴完整密钥并发送，或按 Agent 提示放入密钥配置。
3. 告诉 Agent“继续询价匹配”。

不要手工复制页面上带星号的遮罩文字。已有账号可复制现有密钥；没有可用密钥时，在该页点击“创建 API 密钥”。

API Key 相当于账号密码。请勿把它写进 GitHub、询价文件或公开聊天记录；优先通过 Agent 的密钥配置或环境变量保存。

余额不足时，Agent 会暂停并给出 [钱包充值链接](https://mro-api.iwilley.com/wallet)。在网页充值后告诉 Agent“已充值，继续”，即可从失败处续跑，保留已完成的结果。

### 4. 连接方式

支持远程 MCP 的 Agent 使用：

```text
https://mro-api.iwilley.com/v1/mcp
```

不能注册远程 MCP、但可以运行 Python 3 的 Agent，可使用 Skill 中的 `scripts/mro_api_client.py` 作为 REST 回退。设置 `MRO_API_KEY` 环境变量后，脚本可处理单条匹配、商品详情和本地并发批处理；详细用法见 [可移植性说明](skills/mro-inquiry-match/references/portability.md)。

### 5. 提交询价

单条询价示例：

```text
请使用 MRO 询价匹配 Skill 查找：
六角盖形螺母，M8，A2，DIN 917。
```

带品牌和型号的示例：

```text
请使用 MRO 询价匹配 Skill 查找：
品牌 RS PRO，制造商型号 1234567，不锈钢六角螺母 M8。
```

批量 Excel 示例：

```text
请使用 MRO 询价匹配 Skill 处理这份询价表。
保留原始询价工作表，匹配结果采用可折叠父子行：父行是原始需求，
子行逐件展示首选和备选。前三列为产品名称、描述、规格型号并冻结，
后面展示品牌、制造商编号、单位、数量、单价、状态、平台和依据；
产品名称可点击打开详情页，状态用绿色、黄色、红色及浅橙色区分；
原始标准、备注等附加列保留在末尾，最后导出 Excel。
```

## 结果包含什么

- 首选商品、订货号、品牌和制造商型号
- 商品名称、单价、数据源平台和详情页链接
- 分类和规格匹配依据
- 精确匹配、替代推荐、待确认或未找到状态
- 需要采购或技术人员确认的问题
- 最多 5 个其他匹配项

资料不足以核实关键规格时，Skill 会标记“待确认”，不会直接判定为精确匹配。

## 如何提高匹配准确度

询价内容尽量包含以下信息：

- 产品名称
- 品牌
- 制造商型号或 MPN
- 执行标准
- 尺寸、材质等关键规格
- 不能接受的规格或品牌

客户自己的零件编码也可以保留，但不要把它当作制造商型号。信息不完整时仍可查询，Skill 会列出候选商品及缺少的确认信息。

## 获取帮助

遇到 API Key 无法使用、没有返回候选、分类明显错误、规格筛选未生效或 Excel 无法导出等问题时，请联系平台维护人员，并提供已脱敏的询价内容和错误信息。

请勿在公开 Issue、截图或聊天记录中提交完整 API Key。

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)。

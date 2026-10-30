# 小红书热点×IP内容工作流

基于真实调研的小红书热点×IP内容工作流 Skill，串联选题策划、文案创作、多形式配图与复盘，支持依赖自检补装，让账号人设与视觉风格持续统一。

**流程：调研 → 候选选题 → 用户选择 → 文案与页面方案 → 生图质检 → 归档续跑 → 按需复盘。**

这是一个 Codex Skill，内置依赖自检、缺项补装和连接引导；它不是自动发布软件，也不保证流量。尚未打包为可在插件目录直接安装的 Plugin。

## 能做什么

- 依据小红书公开样本给出最多三个选题，区分近期线索、历史高赞和常青备选。
- 用户选定后完成一个主标题、两个文字备选、正文、匹配话题和有限完整的页面方案。
- 用固定身份参考、本篇首图和逐页检查保持角色与画风一致，局部修复失败页。
- 保存制作进度和实际历史；用户给出发布数据时再复盘。

默认先选题再制作。不会自动登录、发布、评论或安排定时任务。

## 支持的内容形式

漫画/对话小剧场、插画/氛围图文、知识/观点卡片、教程/清单图、生活方式视觉及封面海报。用户指定形式优先；未指定时在候选题中推荐一种并解释理由。角色、品牌视觉与口吻持续统一，页面布局和内容结构不固定。

默认处理静态图文，不因名称扩展而承诺视频、音频或动画生成。[形式选择规则](skills/xiaohongshu-ip-content-studio/references/content-formats.md)

## 使用前准备

| 依赖 | 用途 | 使用者需要准备 |
| --- | --- | --- |
| research-growth-signals | 小红书研究与话题证据 | 已安装技能，已连接自己的 SignalDig MCP |
| xiaohongshu-post-creator | 基于调研写稿 | 已安装技能 |
| imagegen | 最终图片与修复 | 客户端中存在该技能，并实际提供可用的内置生图工具 |

三个依赖源码没有复制进此仓库。首次调用可让本 Skill 自动检查，并通过客户端现有安装器补装两个缺失技能；已安装项会跳过，不自动覆盖或升级。仅安装本 Skill 文件不会执行脚本，补装在你明确要求初始化/安装依赖后进行。

插件连接与授权继续使用客户端原生流程；本 Skill 可查找并建议相关插件，或引导 SignalDig 连接。pending 不等于安装完成，技能文件不等于工具可用，服务授权与额度由使用者自己提供。

- SignalDig 接入与当前安装来源：[官方接入说明](https://signaldig.com/agent-setup)。
- 研究技能：[已核实的 v2.2.0 来源](https://github.com/daily-growth-signals/seo-signal-skills/tree/v2.2.0/skills/research-growth-signals)。
- 小红书写作技能：[上游目录](https://github.com/daily-growth-signals/social-marketing-skills/tree/main/skills/xiaohongshu-post-creator)。
- imagegen 使用客户端提供的当前版本。本项目不会自动改为收费 API 或 CLI。

密钥和账号授权由使用者在自己的客户端连接，不要写进仓库或聊天。

## 安装

### 从 GitHub 安装

仓库发布后，从浏览器地址栏复制仓库主页链接，和下面这段话一起发给 Codex：

    使用 $skill-installer，从我提供的 GitHub 仓库链接安装 skills/xiaohongshu-ip-content-studio。

这会安装仓库中真正的技能目录。仓库应保留展开的 skills/ 文件夹；仅上传 ZIP 不适用于这种安装路径。

### 从源码 ZIP 安装

解压后，将 skills/xiaohongshu-ip-content-studio 文件夹交给 Codex，要求安装到当前客户端实际使用的技能目录。不同客户端目录可能不同，优先使用客户端的技能安装流程，不要求修改配置文件。

克隆本仓库本身不等于已安装技能。安装后确认技能列表可见；如客户端未发现更新，按客户端指引重新加载或开启新聊天。

## 开始使用自己的 IP

    使用 $xiaohongshu-ip-content-studio。
    检查并安装缺失的既定技能依赖。
    我的角色是阿白，一只白狐狸，温和但爱吐槽，蓝白简约漫画风。
    为这个账号研究当前生活热点，先给我有依据的候选选题。

也可以用于没有虚构角色的品牌或栏目，例如：

    使用 $xiaohongshu-ip-content-studio，为我的家居栏目做知识卡片。
    保持米白/深绿配色和简洁字体，不需要拟人主角。先研究选题，选定后再制作。

选定后：

    选第二个，继续完成文案、页面方案和全部图片。

局部修改：

    保留账号设定，只改第 3 张的对白，其他图片继续使用。

复盘：

    复盘这篇笔记发布后 24 小时的数据：阅读1000、赞80、收藏40、评论10。
    曝光和新增关注没有数据。

缺少必要设定时只问关键问题；已经提供的信息会直接写入独立账号档案。也可参考[账号模板](skills/xiaohongshu-ip-content-studio/references/accounts/template.md)。

## 依赖自检与自动补装

可以只完成设置，不开始创作：

    使用 $xiaohongshu-ip-content-studio，检查并安装本工作流缺少的依赖，只做初始化。

也可以只检查，禁止写入：

    使用 $xiaohongshu-ip-content-studio，只检查依赖，不安装。

脚本使用 Python 3 标准库。命令行只读检查：

    python3 skills/xiaohongshu-ip-content-studio/scripts/setup_dependencies.py --check

明确授权并具备客户端目录/网络权限后，补装：

    python3 skills/xiaohongshu-ip-content-studio/scripts/setup_dependencies.py --install

它调用当前客户端的 skill-installer helper，不自建下载器、不执行远程 shell。若 helper/实际技能目录在其他位置，可传 --installer-script、--dest、--skill-root、--skill-path；详见[设置引导](skills/xiaohongshu-ip-content-studio/references/setup.md)与[固定来源清单](skills/xiaohongshu-ip-content-studio/references/dependencies.json)。

检查退出成功只表示检查已完成，不代表服务已认证。工具清单由代理检查后传给脚本；脚本自己不能接触客户端内部工具或替用户授权。

内置 imagegen 需要客户端实际支持。没有内置能力时会保留文案/页面方案并说明图片待完成，不静默安装收费替代品。MCP 密钥只进入受保护字段，不在聊天、脚本参数或仓库中传递。无需新建项目或手改配置。

## 文件保存与换聊天续跑

首次默认归档到实际工作目录的 outputs/xiaohongshu-ip-content-studio/；你也可以直接指定其他目录。该目录按账号和批次分开，包含活动账号档案、索引、选题、成稿、研究记录、页面方案、图片与提示词。

同一工作目录的新聊天可以从索引续跑。换了工作目录时，提供之前的归档根目录，例如：

    使用 $xiaohongshu-ip-content-studio，从我提供的已有归档目录继续上次待选批次。

未给旧位置且当前目录找不到时会询问一次；不会扫描整个主目录，也不承诺跨设备同步。两个批次都存在“第二个”时，会列日期和题名确认。

新安装的制作历史为空，不包含作者的私人研究、分析 ID、账号数据或已制作记录。运行记录由使用者自行保留；.gitignore 已排除默认输出及常见状态文件。

## 从旧名升级

旧名称为 xiaohongshu-ip-studio，新名称为 xiaohongshu-ip-content-studio。旧版源码包和个人历史仍可保留；安装时应由客户端将旧技能目录迁移到新名称，并检查 SKILL.md 与 agents/openai.yaml 同步，避免两个入口同时自动触发。

已有归档不必跟着改名：优先读取明确给定的旧位置。默认目录不存在时，可检查同工作目录的旧 outputs/xiaohongshu-ip-studio/accounts.json；有旧记录就沿用，不初始化空历史。如果新旧目录都已有账号且不明确，询问使用哪一份。

黄小歇现有简约漫画偏好保留，名称变更不重写其人设、素材或历史。

## 黄小歇：只读示例

<img src="skills/xiaohongshu-ip-content-studio/assets/huangxiaoxie/avatar.png" width="180" alt="黄小歇只读角色示例">

示例展示如何约定圆脸、额纹、白斑、角色口吻和漫画画风。它不是安装者默认拥有的账号 IP。

**工作流采用 MIT；黄小歇的角色设定、名称/简介和图片不在 MIT 范围内，另行保留权利。** 可查看示例理解方法，使用自己的角色与参考图。启用黄小歇制作公开内容应另获作者授权；用户明确表示自己是作者或已获授权时，工作流可以继续使用该角色。

详见 [授权范围](LICENSE_SCOPE.md) 与[示例素材说明](skills/xiaohongshu-ip-content-studio/assets/huangxiaoxie/NOTICE.md)。MIT 的宽松复用范围不能当作黄小歇品牌或素材的使用许可。

## 仓库结构

    README.md
    LICENSE
    LICENSE_SCOPE.md
    .gitignore
    scripts/validate_release.py
    skills/xiaohongshu-ip-content-studio/
        SKILL.md
        LICENSE
        LICENSE_SCOPE.md
        agents/openai.yaml
        scripts/setup_dependencies.py
        references/
        assets/huangxiaoxie/

研究接口和图像操作按依赖技能执行；这个仓库没有自建研究 API、发布接口或图像生成服务。agents/openai.yaml 的声明配合设置引导工作，不携带用户凭证，也不保证所有客户端自动完成连接。

## 本地检查

在仓库根目录运行（Python 3，无第三方依赖）：

    python3 scripts/validate_release.py

检查真实文件、相对链接、发布范围、本机路径与常见凭证泄漏、PNG 文件头以及许可文本是否随技能保留。它不会联网、调用 SignalDig、生成图片或发布。

本版同时通过了 skill-creator 的结构校验与离线可移植性演练；这些检查不代表已验证所有客户端、真实生图质量或传播效果。

## 上传 GitHub

1. 创建名为 xiaohongshu-ip-content-studio 的仓库，按分享对象选择公开或私有。
2. 将本目录的展开文件上传到仓库根目录，保留 skills/ 结构；不要上传工作目录中的 outputs/、研究记录或凭证。
3. 将仓库主页链接和上面的安装提示一起发给使用者；如需要，可把版权署名调整为你的公开项目署名。
4. 保留 LICENSE、LICENSE_SCOPE.md 和示例素材说明，再将仓库链接发给使用者。

可以另将源码 ZIP 放进 GitHub Release，但 ZIP 不能取代供安装器读取的展开源码。

## 依赖与参考

- [Codex 技能官方说明](https://learn.chatgpt.com/docs/build-skills)
- [SignalDig 接入说明](https://signaldig.com/agent-setup)
- [SignalDig 社交营销技能仓库](https://github.com/daily-growth-signals/social-marketing-skills)

本项目只分发自身工作流和明确列出的示例资源；第三方依赖按其各自说明与许可使用。

# meeting-classic

基于设计师首版 demo (`meeting.html`) 标准化产出的皮肤模块。

| 项 | 值 |
|---|---|
| 皮肤名 | `meeting-classic` |
| 前缀 | `--mc-*` |
| data-theme | `mc` |
| 原始 demo | `_source/meeting.html` |
| 视觉风格 | 经典白底蓝主色（类似 TRTC / TUIRoom 风） |

## 里程碑进度

- [x] 里程碑 1：盘点 + Token 体系
- [x] 里程碑 2A：原子层 17 个组件
- [x] 里程碑 2B：分子 18 个 + 组织 10 个（累计 45 个组件）
- [x] 里程碑 2C：页面重构 + 像素级还原
- [x] 里程碑 3：校验脚本 + 04/05 SOP
- [x] 里程碑 4：Skill 封装打磨（06 SOP + 3 份 checklist + 2 份 AI prompt）

✅ **全部里程碑完成。Skill 已成为可复用资产。**

## 校验通过证明

```
$ node ../../skills/demo-to-theme/scripts/validate-all.mjs .
✅ scan-hardcoded        0 处违规
✅ scan-inline-style     0 处违规（数据驱动已豁免）
✅ check-token-coverage  100 L2 令牌全覆盖 / 0 L1 直用 / 0 未定义引用
```

## 快速预览

打开以下文件可直接在浏览器查看：

- `index.html` — **重构后的完整会议页面（像素级还原 meeting.html）**
- `components/_preview-atoms.html` — 17 个原子组件总览
- `components/_preview-molecules-organisms.html` — 28 个分子/组织组件总览

## 目录

```
meeting-classic/
├── README.md          # 本文件
├── tokens.css         # 皮肤令牌（L1 + L2）
├── components/        # 组件样式（里程碑 2 产出）
├── layout.css         # 页面骨架（里程碑 3 产出）
├── index.css          # 汇总入口（里程碑 3 产出）
├── index.html         # 重构后 HTML（里程碑 3 产出）
├── _audit/            # 盘点与校验
│   └── inventory.md   # 盘点报告
└── _source/           # 原始 demo 归档
    └── meeting.html
```

## 接入方式

```html
<html data-theme="mc">
<head>
  <link rel="stylesheet" href="themes/meeting-classic/index.css">
</head>
```

## 令牌统计

- L1 皮肤私有令牌：约 100 个
- L2 通用别名：91 个（与 `shared/token-schema.md` 对齐）

## 参考

- 盘点报告：[`_audit/inventory.md`](./_audit/inventory.md)
- 令牌契约：[`../../shared/token-schema.md`](../../shared/token-schema.md)
- 处理流水线：[`../../skills/demo-to-theme/SKILL.md`](../../skills/demo-to-theme/SKILL.md)

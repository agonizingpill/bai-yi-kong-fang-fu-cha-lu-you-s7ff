        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "空房联系人与访问授权",
  "module": "空房与授权簿",
  "caption": "空房与授权簿",
  "detail": "使用归档代号管理空房联系人。拒入后需要房主书面重新授权，不能沿用先前的批准。",
  "path": "/vacant_rooms",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "building",
      "label": "业主单位"
    },
    {
      "name": "room",
      "label": "空房门牌"
    },
    {
      "name": "contact_ref",
      "label": "归档联系人"
    },
    {
      "name": "key_tag",
      "label": "钥匙牌"
    },
    {
      "name": "permit_ref",
      "label": "书面授权"
    },
    {
      "name": "permit_until",
      "label": "授权截止"
    },
    {
      "name": "status",
      "label": "授权状态"
    }
  ],
  "layout": "flip",
  "view": "stack",
  "actions": [
    {
      "name": "renew_permit",
      "label": "录入房主重新授权",
      "path": "/vacant_rooms/renew-permit",
      "fields": [
        {
          "name": "room_code",
          "label": "空房编号",
          "kind": "text",
          "initial": "ROOM-17"
        },
        {
          "name": "permit_ref",
          "label": "房主书面授权号",
          "kind": "text",
          "initial": "AUTH-NEW-17"
        },
        {
          "name": "permit_until",
          "label": "许可截止 YYYY-MM-DD",
          "kind": "text",
          "initial": "2090-05-10"
        },
        {
          "name": "witness",
          "label": "确认人",
          "kind": "text",
          "initial": "邹允复核"
        }
      ],
      "help": "房主授权版本变更后，已有交接单还会核验授权快照。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "vacant_rooms";
        export async function render(root, role) {
          await workspace(root, role, page);

        }

        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "重新复约 · 钥匙交接簿",
  "module": "再授权与钥匙交接",
  "caption": "再授权与钥匙交接",
  "detail": "复访计划需目标日期授权和本房照片回执；承诺后交钥匙时再次检查授权。",
  "path": "/key_handoffs",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "room_code",
      "label": "空房"
    },
    {
      "name": "forecast",
      "label": "复查签认"
    },
    {
      "name": "proof_visit",
      "label": "照片来源观察"
    },
    {
      "name": "photo_receipt",
      "label": "照片回执"
    },
    {
      "name": "same_room_receipt",
      "label": "同房回执"
    },
    {
      "name": "permit_snapshot",
      "label": "本次书面授权快照"
    },
    {
      "name": "visit_date",
      "label": "拟交接日期"
    },
    {
      "name": "key_tag",
      "label": "钥匙交接牌"
    },
    {
      "name": "team_member",
      "label": "带钥负责人"
    },
    {
      "name": "status",
      "label": "交接状态"
    },
    {
      "name": "receipt",
      "label": "钥匙回单"
    }
  ],
  "layout": "flip",
  "view": "table",
  "actions": [
    {
      "name": "book_revisit",
      "label": "复约并登记照片回执",
      "path": "/key_handoffs/book-revisit",
      "fields": [
        {
          "name": "code",
          "label": "钥匙复约编号",
          "kind": "text",
          "initial": "KEYPLAN-QA"
        },
        {
          "name": "forecast",
          "label": "复查签认",
          "kind": "text",
          "initial": "FC-QA"
        },
        {
          "name": "proof_visit",
          "label": "照片来源观察",
          "kind": "text",
          "initial": "V-ZERO-QA"
        },
        {
          "name": "photo_receipt",
          "label": "核验照片回执",
          "kind": "text",
          "initial": "PHOTO-QA-ZERO"
        },
        {
          "name": "team_member",
          "label": "带钥负责人",
          "kind": "text",
          "initial": "陈溪"
        }
      ],
      "help": "核过房主授权后，验证最近现场的观察回执。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "release_key",
      "label": "签出钥匙",
      "path": "/key_handoffs/release-key",
      "fields": [
        {
          "name": "handoff",
          "label": "交接号",
          "kind": "text",
          "initial": "KEYPLAN-QA"
        },
        {
          "name": "key_tag",
          "label": "现场钥匙牌",
          "kind": "text",
          "initial": "KEY-017"
        }
      ],
      "help": "实际交钥匙前核对授权快照和实物挂牌。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "return_key",
      "label": "登记归还回执",
      "path": "/key_handoffs/return-key",
      "fields": [
        {
          "name": "handoff",
          "label": "交接号",
          "kind": "text",
          "initial": "KEYPLAN-QA"
        },
        {
          "name": "receipt",
          "label": "钥匙归还回单",
          "kind": "text",
          "initial": "KEYRET-017"
        }
      ],
      "help": "柜台核对回单编号，签归还。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "change_receipt",
      "label": "复约换同房回执 / 更换照片来源",
      "path": "/key_handoffs/change-receipt",
      "fields": [
        {
          "name": "handoff",
          "label": "交接/复约号",
          "kind": "text",
          "initial": "KEYPLAN-QA"
        },
        {
          "name": "proof_visit",
          "label": "同房照片来源观察",
          "kind": "text",
          "initial": "V-ZERO-QA"
        },
        {
          "name": "photo_receipt",
          "label": "核验照片回执",
          "kind": "text",
          "initial": "PHOTO-QA-ZERO"
        },
        {
          "name": "forecast",
          "label": "新签认估计（失效重算后填写）",
          "kind": "text",
          "initial": "",
          "required": false
        }
      ],
      "help": "原照片转走后，未签出的复约必须改挂本房观察回执；若旧估计失效，同时填入新签认估计后再签出钥匙。已借出的钥匙仍按原单归还。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已更换"
    },
    {
      "name": "cancel_booking",
      "label": "撤销未签出复约",
      "path": "/key_handoffs/cancel-booking",
      "fields": [
        {
          "name": "handoff",
          "label": "交接号",
          "kind": "text",
          "initial": "KEYPLAN-QA"
        }
      ],
      "help": "授权更新后撤销尚未交钥匙的旧复约，保留历史并释放复查签认。",
      "roles": [
        "reviewer"
      ],
      "success": "已撤销"
    }
  ]
};

        export const {title} = page;
        export const key = "key_handoffs";
        export async function render(root, role) {
          await workspace(root, role, page);

        }

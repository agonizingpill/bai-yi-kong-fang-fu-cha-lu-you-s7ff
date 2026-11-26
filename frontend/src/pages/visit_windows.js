        import {workspace} from '../workspace.js';
        import {visitDocket} from '../visit-docket.js';

        const page = {
  "title": "观察记录 · 实见零与拒入",
  "module": "观察窗口与拒入",
  "caption": "观察窗口与拒入",
  "detail": "实见计数必须有照片回执。拒入只能记录为未观测，并触发重新授权。",
  "path": "/visit_windows",
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
      "name": "visit_day",
      "label": "预约日期"
    },
    {
      "name": "activity_count",
      "label": "实见活动数"
    },
    {
      "name": "status",
      "label": "观察状态"
    },
    {
      "name": "photo_receipt",
      "label": "照片回执"
    },
    {
      "name": "desk_note",
      "label": "观察或拒入记录"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "record_count",
      "label": "登记已进房实见数",
      "path": "/visit_windows/record-count",
      "fields": [
        {
          "name": "code",
          "label": "观察窗号",
          "kind": "text",
          "initial": "V-ZERO-QA"
        },
        {
          "name": "room_code",
          "label": "空房编号",
          "kind": "text",
          "initial": "ROOM-17"
        },
        {
          "name": "visit_day",
          "label": "实际观察日期",
          "kind": "text",
          "initial": "2090-03-22"
        },
        {
          "name": "activity_count",
          "label": "实见活动数",
          "kind": "int",
          "initial": 0
        },
        {
          "name": "photo_receipt",
          "label": "照片文件回执",
          "kind": "text",
          "initial": "PHOTO-QA-ZERO"
        },
        {
          "name": "desk_note",
          "label": "观察备注",
          "kind": "text",
          "initial": "允许进房，实见零"
        }
      ],
      "help": "明示 0 表示已经进房核验。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "register_refusal",
      "label": "登记房主拒入",
      "path": "/visit_windows/register-refusal",
      "fields": [
        {
          "name": "code",
          "label": "观察窗号",
          "kind": "text",
          "initial": "V-REFUSE-QA"
        },
        {
          "name": "room_code",
          "label": "空房编号",
          "kind": "text",
          "initial": "ROOM-17"
        },
        {
          "name": "visit_day",
          "label": "预约日期",
          "kind": "text",
          "initial": "2090-03-24"
        },
        {
          "name": "desk_note",
          "label": "拒入情况",
          "kind": "text",
          "initial": "房主确认本次不能进房"
        }
      ],
      "help": "不能把拒入填写为活动数 0；同时挂起该空房的访问权。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "transfer_record",
      "label": "转记/转移到正确房间：实见数和原照片回执",
      "path": "/visit_windows/transfer-record",
      "fields": [
        {
          "name": "code",
          "label": "要转走的观察窗号",
          "kind": "text",
          "initial": "V-ZERO-QA"
        },
        {
          "name": "room_code",
          "label": "正确空房编号",
          "kind": "text",
          "initial": "ROOM-22"
        }
      ],
      "help": "实见数与原 PHOTO 回执整体转到正确房间；正确房间当天已有窗口会整笔退回。两房目标日复访估计失效，须重新计算并签认。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已转记"
    }
  ]
};

        export const {title} = page;
        export const key = "visit_windows";
        export async function render(root, role) {
          await workspace(root, role, page);
          await visitDocket(root);

        }

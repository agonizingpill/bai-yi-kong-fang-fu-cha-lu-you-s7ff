        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "时间留出与复查间隔",
  "module": "复访间隔簿",
  "caption": "复访间隔簿",
  "detail": "用最近一次实际计数构造滞后量。只使用复访日前的实见数据，日期按观察后才能重算的顺序留出。",
  "path": "/return_forecasts",
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
      "name": "target_day",
      "label": "拟复访日期"
    },
    {
      "name": "prediction",
      "label": "估计实见活动数"
    },
    {
      "name": "lag_count",
      "label": "最近一次实见值"
    },
    {
      "name": "gap_days",
      "label": "距最近实见天数"
    },
    {
      "name": "holdout_mae",
      "label": "末段留出 MAE"
    },
    {
      "name": "skipped_refusals",
      "label": "跳过的拒入窗口数"
    },
    {
      "name": "token",
      "label": "后台评估凭证"
    }
  ],
  "layout": "split",
  "view": "grid",
  "actions": [
    {
      "name": "fit_return",
      "label": "计算下次复访估计",
      "path": "/return_forecasts/fit-return",
      "fields": [
        {
          "name": "room_code",
          "label": "空房编号",
          "kind": "text",
          "initial": "ROOM-17"
        },
        {
          "name": "target_day",
          "label": "拟复访日期",
          "kind": "text",
          "initial": "2090-04-05"
        }
      ],
      "help": "可先估计再向房主复约。拒入记录只增加跳过计数。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "sign_return",
      "label": "签认复查间隔",
      "path": "/return_forecasts/sign-return",
      "fields": [
        {
          "name": "code",
          "label": "签认凭证",
          "kind": "text",
          "initial": "FC-QA"
        },
        {
          "name": "token",
          "label": "后台评估凭证",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "将回归训练、留出误差和最近实见间隔固化。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "return_forecasts";
        export async function render(root, role) {
          await workspace(root, role, page);

        }

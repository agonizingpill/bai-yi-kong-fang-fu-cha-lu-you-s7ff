import {el} from './dom.js';
import {request} from './api.js';

export async function visitDocket(root) {
  const [rooms, windows] = await Promise.all([request('/vacant_rooms'),request('/visit_windows')]);
  const area = el('section',{class:'visit-docket'},
    el('h2',{},'实见与未观测 · 逐日夹页'));
  const selector = el('select',{'aria-label':'选择空房'},rooms.map((room) =>
    el('option',{value:room.code},room.building+' · '+room.room)));
  const strip = el('ul',{'aria-label':'按日观察记录'});
  function render() {
    const rows=windows.filter((item)=>item.room_code===selector.value)
      .sort((a,b)=>a.visit_day.localeCompare(b.visit_day)).slice(-16);
    strip.replaceChildren(...rows.map((item)=>{
      const type=item.status==='拒入未观测'?'refused':item.activity_count===0?'zero':'';
      return el('li',{class:type,title:item.desk_note},el('time',{},item.visit_day.slice(5)),
        el('br',{}),el('strong',{},type==='refused'?'拒入 · 未观测':'实见 '+item.activity_count));
    }));
  }
  selector.addEventListener('change',render);
  area.append(selector,strip);
  root.querySelector('.ledger')?.before(area);
  render();
}

"""Add deep analysis to frontend + fix Q1 display"""
import json

with open(r'C:\soft\agent\ai-dashboard\web\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add deep analysis section after Q1 section
old_q1 = '</div>\n	    </div>\n\n	    <div class="detail-section">\n	      <h3>📰 最新动态与解读</h3>'
new_q1 = '''</div>

	    <div class="detail-section">
	      <h3>🔬 深度产品技术分析</h3>
	      <div id="deepContent" style="font-size:12px;line-height:1.8">--</div>
	    </div>

	    <div class="detail-section">
	      <h3>📰 最新动态与解读</h3>'''

if old_q1 in html:
    html = html.replace(old_q1, new_q1)
    print('Deep analysis section added')
else:
    print('Could not find insertion point')

# 2. Add JS to populate deep analysis + Q1 data
old_js = "  }, 100);"
new_js = """  }, 100);

  // Populate deep analysis
  setTimeout(() => {
    const da = stock.deep_analysis;
    if (!da) return;
    const dc = document.getElementById('deepContent');
    if (!dc) return;
    let h = '';
    if (da.products && da.products.length > 0) {
      h += '<div style="margin-bottom:6px;color:var(--text2)">产品矩阵:</div>';
      da.products.forEach(p => {
        const icon = p.status.includes('量产') ? '✅' : p.status.includes('研发') ? '🔬' : '❌';
        h += '<div style="margin:2px 0">'+icon+' <b>'+p.name+'</b> <span style="color:var(--text2)">['+p.status+']</span> '+p.detail+'</div>';
      });
    }
    if (da.supply_chain) {
      h += '<div style="margin-top:8px;color:var(--text2)">供应链:</div>';
      h += '<div>上游: '+da.supply_chain.upstream+'</div>';
      h += '<div>下游: '+da.supply_chain.downstream+'</div>';
      h += '<div>定位: '+da.supply_chain.position+'</div>';
    }
    if (da.catalysts && da.catalysts.length > 0) {
      h += '<div style="margin-top:8px;color:var(--green)">催化:</div>';
      da.catalysts.forEach(c => { h += '<div>+ '+c+'</div>'; });
    }
    if (da.risks && da.risks.length > 0) {
      h += '<div style="margin-top:8px;color:var(--red)">风险:</div>';
      da.risks.forEach(r => { h += '<div>- '+r+'</div>'; });
    }
    if (da.key_question) {
      h += '<div style="margin-top:8px;padding:6px;background:rgba(79,143,255,.08);border-radius:4px;color:var(--accent)">❓ '+da.key_question+'</div>';
    }
    dc.innerHTML = h || '--';
  }, 150);

  // Populate Q1 data
  setTimeout(() => {
    ['q1rev','q1prof','q1gm','q1ryoy'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (id === 'q1rev' && stock.q1_revenue != null) {
        el.textContent = stock.q1_revenue ? stock.q1_revenue.toFixed(2)+'亿' : '--';
      }
      if (id === 'q1prof' && stock.q1_profit != null) {
        el.textContent = stock.q1_profit ? stock.q1_profit.toFixed(2)+'亿' : '--';
        el.style.color = stock.q1_profit >= 0 ? 'var(--green)' : 'var(--red)';
      }
      if (id === 'q1gm' && stock.q1_gross_margin != null) {
        el.textContent = stock.q1_gross_margin ? stock.q1_gross_margin.toFixed(1)+'%' : '--';
      }
      if (id === 'q1ryoy' && stock.q1_revenue_yoy != null) {
        const v = stock.q1_revenue_yoy;
        el.textContent = v ? (v>0?'+':'')+v.toFixed(1)+'%' : '--';
        el.style.color = v >= 0 ? 'var(--green)' : 'var(--red)';
      }
    });
  }, 200);"""

html = html.replace(old_js, new_js)
print('JS updated')

with open(r'C:\soft\agent\ai-dashboard\web\index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Frontend updated')

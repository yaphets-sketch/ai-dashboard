"""Add Q1 financial data to the detail panel"""
import re

with open(r'C:\soft\agent\ai-dashboard\web\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the line after revenue_detail and before concept section
# Insert Q1 revenue/profit rows
old = "标签与业务无关"
new = """标签与业务无关
      </div>
    </div>

    <div class="detail-section">
      <h3>📊 最新财报 (2026Q1)</h3>
      <div class="info-row"><span class="label">Q1营收</span><span class="val" id="q1rev">--</span></div>
      <div class="info-row"><span class="label">Q1净利润</span><span class="val" id="q1prof">--</span></div>"""

content = content.replace(old, new)

# Now add the JS to populate Q1 data in showDetail
# Find the showDetail function and add Q1 data population
old2 = "document.getElementById('detailPanel').innerHTML = detailHTML;"
new2 = """document.getElementById('detailPanel').innerHTML = detailHTML;
  // Populate Q1 data
  setTimeout(() => {
    const q1rev = document.getElementById('q1rev');
    const q1prof = document.getElementById('q1prof');
    if (q1rev && stock.q1_revenue != null) {
      q1rev.textContent = stock.q1_revenue ? stock.q1_revenue.toFixed(0) + '亿' : '--';
    }
    if (q1prof && stock.q1_profit != null) {
      q1prof.textContent = stock.q1_profit ? stock.q1_profit.toFixed(2) + '亿' : '--';
      if (stock.q1_profit < 0) q1prof.style.color = 'var(--red)';
      else q1prof.style.color = 'var(--green)';
    }
  }, 100);"""

content = content.replace(old2, new2)

with open(r'C:\soft\agent\ai-dashboard\web\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Frontend updated: Q1 financial data section added")

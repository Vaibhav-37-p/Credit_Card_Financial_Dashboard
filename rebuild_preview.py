from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.labelcolor':'#41556d','xtick.color':'#41556d','ytick.color':'#41556d','text.color':'#102f50','axes.titleweight':'bold'})
BLUE='#2467a2'; LIGHT='#89b6df'; TEAL='#169c9a'; BG='#eff5fb'
def canvas(title,subtitle):
 f=plt.figure(figsize=(16,10),facecolor=BG)
 f.text(.045,.94,title,fontsize=27,weight='bold')
 f.text(.045,.906,subtitle,fontsize=11,color='#41556d')
 return f
def cards(f,items):
 for i,(label,value,detail) in enumerate(items):
  x=.045+i*.235
  f.patches.append(FancyBboxPatch((x,.76),.218,.112,boxstyle='round,pad=0.009',transform=f.transFigure,facecolor='white',edgecolor='#d5e2f1',zorder=-1))
  f.text(x+.01,.84,label,fontsize=10,weight='bold')
  f.text(x+.01,.795,value,fontsize=25,weight='bold')
  f.text(x+.01,.772,detail,fontsize=8,color='#526b86')
def panel(f,pos,title):
 a=f.add_axes(pos,facecolor='white');a.set_title(title,loc='left',pad=16,fontsize=13);a.grid(axis='x',alpha=.12);a.set_axisbelow(True);return a
def bars(a,s,color=BLUE,million=True):
 s=s.sort_values(); vals=s.values/(1e6 if million else 1)
 a.barh(s.index.astype(str),vals,color=color,height=.6);a.set_xlim(0,max(vals)*1.22)
 for i,v in enumerate(vals):a.text(v+max(vals)*.025,i,f'{v:,.2f}M' if million else f'{v:,.0f}',va='center',fontsize=9)
 a.tick_params(axis='y',length=0);a.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'+('M' if million else '')))
def save(f,name):
 f.savefig(ROOT/(name+'.png'),dpi=125,facecolor=f.get_facecolor())
 f.savefig(ROOT/(name+'.pdf'),facecolor=f.get_facecolor())
 plt.close(f)

# Append the update files, align the transaction-count header and validate a 1:1 join.
a=pd.read_csv(ROOT/'credit_card.csv');b=pd.read_csv(ROOT/'cc_add.csv').rename(columns={'Total_Trans_Ct':'Total_Trans_Vol'})
c=pd.read_csv(ROOT/'customer.csv');e=pd.read_csv(ROOT/'cust_add.csv')
cc=pd.concat([a,b],ignore_index=True);cu=pd.concat([c,e],ignore_index=True)
assert cc.Client_Num.is_unique and cu.Client_Num.is_unique
assert set(cc.Client_Num)==set(cu.Client_Num)
d=cc.merge(cu,on='Client_Num',validate='one_to_one')
d['Revenue']=d.Total_Trans_Amt+d.Annual_Fees+d.Interest_Earned
d['Week_Start_Date']=pd.to_datetime(d.Week_Start_Date,format='%d-%m-%Y')
assert len(d)==10293
metrics={'records':len(d),'revenue':float(d.Revenue.sum()),'interest':float(d.Interest_Earned.sum()),'transaction_amount':int(d.Total_Trans_Amt.sum()),'transactions':int(d.Total_Trans_Vol.sum()),'customer_income_sum':int(d.Income.sum()),'satisfaction_mean':float(d.Cust_Satisfaction_Score.mean()),'start':str(d.Week_Start_Date.min().date()),'end':str(d.Week_Start_Date.max().date())}
(ROOT/'verified_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
for name,col in [('card_category','Card_Category'),('quarter','Qtr'),('state','state_cd'),('job','Customer_Job'),('expenditure','Exp Type'),('gender','Gender')]:
 d.groupby(col).agg(revenue=('Revenue','sum'),transaction_amount=('Total_Trans_Amt','sum'),transaction_count=('Total_Trans_Vol','sum'),records=('Client_Num','size')).to_csv(ROOT/('summary_'+name+'.csv'),float_format='%.2f')
f=canvas('Credit Card | Transaction Performance','2023 portfolio snapshot | Base + additional records | Monetary values shown in source units')
cards(f,[('Project revenue metric',f'{metrics["revenue"]/1e6:.2f}M','Transaction amount + fees + interest'),('Interest earned',f'{metrics["interest"]/1e6:.2f}M','Source monetary units'),('Transaction amount',f'{metrics["transaction_amount"]/1e6:.2f}M','Source monetary units'),('Transaction count',f'{metrics["transactions"]:,}','Sum of recorded transaction volumes')])
a=panel(f,[.115,.44,.35,.225],'Revenue by card category');bars(a,d.groupby('Card_Category').Revenue.sum())
a=panel(f,[.60,.44,.34,.225],'Revenue by expenditure category');bars(a,d.groupby('Exp Type').Revenue.sum(),TEAL)
a=panel(f,[.115,.105,.35,.225],'Quarterly revenue');q=d.groupby('Qtr').Revenue.sum()/1e6;a.bar(q.index,q.values,color=BLUE,width=.55);a.set_ylim(0,q.max()*1.18);a.set_ylabel('Revenue (millions)')
for i,v in enumerate(q):a.text(i,v+.15,f'{v:.2f}M',ha='center',fontsize=10)
a=panel(f,[.60,.105,.34,.225],'Revenue by transaction method');bars(a,d.groupby('Use Chip').Revenue.sum(),TEAL)
f.text(.045,.035,'Revenue is a project-specific composite, not bank revenue or profit. Source CSVs do not specify currency; no FX conversion applied.',fontsize=9,color='#526b86')
save(f,'Dashboard_Transaction')
f=canvas('Credit Card | Customer Profile','2023 portfolio snapshot | 10,293 matched records | Monetary values shown in source units')
cards(f,[('Project revenue metric',f'{metrics["revenue"]/1e6:.2f}M','Same population as transaction view'),('Customer records',f'{len(d):,}','One row per Client_Num'),('Recorded customer income',f'{metrics["customer_income_sum"]/1e6:.2f}M','Sum of income; period unspecified'),('Mean satisfaction score',f'{metrics["satisfaction_mean"]:.2f}','Observed scores 1–5; anchors unknown')])
state=d.groupby('state_cd').Revenue.sum().sort_values(ascending=False)
state_display=state.head(5).copy();state_display.loc['Other states']=state.iloc[5:].sum()
a=panel(f,[.115,.44,.35,.225],'Revenue by state | top 5 + other');bars(a,state_display)
a=panel(f,[.60,.44,.34,.225],'Revenue by occupation');bars(a,d.groupby('Customer_Job').Revenue.sum(),TEAL)
a=panel(f,[.115,.105,.35,.225],'Revenue by gender');bars(a,d.groupby('Gender').Revenue.sum().rename(index={'F':'Female','M':'Male'}))
d['Age group']=pd.cut(d.Customer_Age,[0,29,39,49,59,200],labels=['Under 30','30–39','40–49','50–59','60+'])
a=panel(f,[.60,.105,.34,.225],'Revenue by age group');bars(a,d.groupby('Age group',observed=False).Revenue.sum(),TEAL)
f.text(.045,.035,'Group totals reflect both customer counts and recorded values. They do not establish lifetime value, churn risk or market opportunity.',fontsize=9,color='#526b86')
save(f,'Dashboard_Customer')
# Keep existing PDF filenames aligned with the revised images.
import shutil
shutil.copyfile(ROOT/'Dashboard_Transaction.pdf',ROOT/'Credit_Card_Transaction_Report.pdf')
shutil.copyfile(ROOT/'Dashboard_Customer.pdf',ROOT/'Credit_Card_Report_Customer.pdf')
print(json.dumps(metrics,indent=2))

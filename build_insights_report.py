"""Build the revised insights PDF after running rebuild_preview.py."""
from pathlib import Path
import json
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
R=Path(__file__).resolve().parent
m=json.loads((R/'verified_metrics.json').read_text())
card=pd.read_csv(R/'summary_card_category.csv').set_index('Card_Category')
quarter=pd.read_csv(R/'summary_quarter.csv').set_index('Qtr')
blue=card.loc['Blue','revenue'];share=blue/m['revenue']*100
styles=getSampleStyleSheet()
styles['Title'].textColor=colors.HexColor('#143858')
styles['BodyText'].fontSize=10;styles['BodyText'].leading=15
story=[]
def p(t,style='BodyText'):story.append(Paragraph(t,styles[style]));story.append(Spacer(1,10))
p('Credit Card Performance & Insights','Title')
p('2023 portfolio dataset | Base and additional records | Source monetary units')
p('Verified performance','Heading2')
rows=[['Metric','Value'],['Matched customer records',f"{m['records']:,}"],['Project revenue metric',f"{m['revenue']:,.2f}"],['Transaction amount',f"{m['transaction_amount']:,}"],['Interest earned',f"{m['interest']:,.2f}"],['Transaction count',f"{m['transactions']:,}"],['Mean satisfaction score',f"{m['satisfaction_mean']:.2f}"]]
t=Table(rows,colWidths=[300,170]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#2467a2')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eff5fb'),colors.white]),('PADDING',(0,0),(-1,-1),9),('ALIGN',(1,1),(1,-1),'RIGHT')]))
story += [t,Spacer(1,16)]
p('What the results support','Heading2')
p(f'<b>Card mix:</b> Blue cards contribute {blue/1e6:.2f}M, or {share:.1f}% of the project revenue metric. Review concentration alongside per-customer values and costs before making product decisions.')
p(f'<b>Quarterly pattern:</b> Q4 records the highest quarterly project revenue, {quarter.loc["Q4","revenue"]/1e6:.2f}M. The figures do not establish holiday effects or profit-margin changes.')
p('<b>Customer comparisons:</b> Segment totals are useful for describing the customer base. Their differences do not establish lifetime value, retention risk or untapped market opportunity.')
p('Definitions and limits','Heading2')
p('Project revenue = transaction amount + annual fees + interest earned. This composite reproduces the project metric; it is not recognised bank revenue or profit. CSV rows are client-level snapshot records with aggregated transaction counts, not individual purchases.')
p('The CSVs do not identify currency, so neither pound nor dollar symbols are used. Satisfaction values range from 1 to 5, but response labels and benchmarks are not documented. The observed mean cannot establish dissatisfaction or churn.')
p('Source: credit_card.csv + cc_add.csv and customer.csv + cust_add.csv. Update count headers are aligned before appending. Client_Num is unique on each side and the join is validated one-to-one. See rebuild_preview.py and summary CSVs for calculations.')
SimpleDocTemplate(str(R/'Credit_Card_Professional_Insights_Report.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=36).build(story)

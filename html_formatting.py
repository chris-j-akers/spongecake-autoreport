import premailer
import data_columns

def master_font():
    return 'Noto Sans'

def header():
    return '<body>'

def footer():
    return '</body>'

def company_header(company_title):
    return '<div style="font-weight: bold;"><hr>{company_title}<hr></div>'.format(company_title=company_title)

def company_footer():
    return '<p/>'

def chart(img_id, height='400px', width='1500px'):
    html = '<div style="text-align: center;"><img src=cid:{img_id} height={height} width={width} style="border: 1px solid black"></div>'.format(img_id=img_id,height=height,width=width, font_family=master_font())
    return html

def fundamentals(fundamentals):
    html = '<div style="font-family: Courier;">'
    html = '<p>'
    for key in fundamentals.keys():
        if key not in [data_columns.FundamentalsDataColumns.COL_DATE_OF_LATEST_INCOME_SHEET, data_columns.FundamentalsDataColumns.COL_DATE_OF_LAST_BALANCE_SHEET]:
            html += '<strong>{0}:</strong> {1:,.2f}'.format(key, float(fundamentals[key]))
        else:
            html += '<strong>{0}:</strong> {1}'.format(key, fundamentals[key])
        html += '<br/>'
    html += '</p>'
    html += '</div>'
    return html


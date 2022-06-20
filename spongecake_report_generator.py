from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class SpongecakeReportGenerator:

    '''
    Class used to generate HTML for the Report.

    Contains various HTML and CSS formatting functions and functions to generate
    the complete HTML and PDF files using Weasyprint.
    '''
    
    font_family = 'Noto Sans'
    font_url = 'https://fonts.googleapis.com/css?family=Noto+Sans'

    def page_css(self):
        return CSS(string = '''
            @page {
            size: A4; /* Change from the default size of A4 */
            margin: 1cm; /* Set margin on each page */
            }
        ''')        

    def table_css(self):
        return CSS(string = '''
            table {
                border-collapse: collapse;
                border: 1px solid gray;
                margin: 2px;
                font-size: 5px;
                display: inline-block;
                vertical-align: top;
            }
        ''')


    def th_css(self):
        return CSS(string = '''
            th {
                font-size: 5px;
                text-align: left;
                font-weight: bold;
                border: 1px solid gray;
                padding: 2px;
                border-spacing: 5px;
            }
        ''')

    def td_css(self):
        return CSS(string = '''
            td {
                font-size: 5px;
                text-align: left;
                border: 1px solid gray;
                padding: 2px;
                border-spacing: 5px;
            }
        ''')


    def table_block_css(self):
        return CSS(string = '''
            .table_block {
                text-align: center;
                margin-left: auto;
                margin-right: auto;
                width: 100%;
            }
        ''')

    def page_css(self):
        return CSS(string = '''
            @page {
                size:A4;
                margin:0;
            }
        ''' )

    def font_css(self):
        return CSS(string = '''
            @font-face {{
                font-family: {font_family};
                font-style: normal;
                src: url({font_url});
            }}
        '''.format(font_url='https://fonts.googleapis.com/css?family=Noto+Sans',
                font_family='Noto Sans'))


    def body_css(self):
        return CSS(string = '''
            body {{
                font-family: {font_family};
            }}
        '''.format(font_family='Noto Sans'))


    def img_css(self):
        return CSS(string = '''
            img {
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 100%;
            }
        ''')

    def company_block_css(self):
        return CSS(string = '''
            .company_block {
                page-break-after: always; 
            }
        ''')

    def company_description_css(self):
        return CSS(string = '''
            .company_description {
                font-size: 10px;
                font-style: italic;
            }
        ''')

    def html_template(self, title, description, income_html_table, balance_html_table, summary_html_table, calcs_table, chart_img_path):
        return '''
            <html>
                <head>
                </head>
                <body>
                    <div>
                        <h3>{title}</h3>
                    </div>
                    </p>
                        <hr>
                    </p>
                    <div class="company_description">
                        <p>
                            {company_description}
                        </p>
                    </div>
                    </p>
                    <hr>
                    </p>
                    <div class="company_block">
                        <div>
                            <img src='{chart_img_path}'/>
                        </div>
                        <p/>
                        <hr>
                        <p/>
                        <div class="table_block">
                            <table style="border-collapse: collapse; border: none; margin: 0px;">
                                <tr>
                                    <td style="border: none; padding: 0px";>
                                        {summary_table}
                                        <p/>
                                        <hr>
                                        <p/>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="border: none; padding: 0px">
                                        {calcs_table}
                                    </td>
                                </tr>
                            </table>
                            {income_table}
                            {balance_table}
                        </div>
                    </div>
                <body>
            </html>
            '''.format(income_table = income_html_table,
                    balance_table = balance_html_table,
                    summary_table = summary_html_table,
                    calcs_table = calcs_table,
                    chart_img_path = chart_img_path,
                    title=title,
                    company_description=description)

    def generate_html(self, title, description, chart_img_filename, income_table, balance_table, summary_table, calcs_table):
        '''
        Produce full page of HTML consisting of company charts and other
        statistics ready for conversion to PDF.

        Parameters:

            title: Page Title
            description: Description of the instrument
            chart_img_filename: Full path to the location of the chart image
            income_table: Dataframe containing income data
            balance_table: Dataframe containing balance data
            summary_table: Dataframe containing summary data
            calcs_table: Dataframe containing  various extra calculations

        Returns

            String of HTML formatted data for this particular report page
        '''

        income_table = income_table.reset_index()
        income_table['Income Line Item'] = income_table['Income Line Item'].str.upper()
        income_table.columns = map(str.upper, income_table.columns)

        balance_table = balance_table.reset_index()
        balance_table['Balance Line Item'] = balance_table['Balance Line Item'].str.upper()
        balance_table.columns = map(str.upper, balance_table.columns)

        summary_table = summary_table.reset_index()
        summary_table['Summary Line Item'] = summary_table['Summary Line Item'].str.upper()
        summary_table.columns = map(str.upper, summary_table.columns)

        income_table_html = income_table.to_html(index=False)
        balance_table_html = balance_table.to_html(index=False)
        summary_table_html = summary_table.to_html(index=False)
        calcs_table_html = calcs_table.to_html(index=False)

        raw_html = self.html_template(title, description, income_table_html, balance_table_html, summary_table_html, calcs_table_html, chart_img_filename)
        return raw_html

    def generate_pdf(self, path, raw_html):

        '''
        Generate PDF file from raw_html using Weasyprint.

        Parameters:

            path: Where to save the output PDF file
            raw_html: String of HTML to convert
        '''

        font_config = FontConfiguration()
        HTML(string=raw_html).write_pdf('{0}.pdf'.format(path),stylesheets=[self.font_css(), 
                                                                            self.page_css(),
                                                                            self.table_block_css(),
                                                                            self.table_css(), 
                                                                            self.img_css(),
                                                                            self.td_css(), 
                                                                            self.th_css(),
                                                                            self.body_css(),
                                                                            self.company_block_css(),
                                                                            self.company_description_css()],
                                                                            font_config=font_config)





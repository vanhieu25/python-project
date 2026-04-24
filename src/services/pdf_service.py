"""
PDF Service Module
Service for generating PDF from contracts.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from services.template_service import TemplateService, TemplateResult


class PDFService:
    """Service for PDF generation operations.

    Note: This is a simplified version that generates HTML.
    For actual PDF generation, integrate with WeasyPrint or ReportLab.
    """

    def __init__(self, template_service: TemplateService):
        """Initialize service.

        Args:
            template_service: Template service instance
        """
        self.template_service = template_service

    def generate_contract_pdf(
        self,
        contract_id: int,
        template_id: int = None,
        include_watermark: bool = False
    ) -> TemplateResult:
        """Generate PDF for contract.

        Args:
            contract_id: Contract ID
            template_id: Optional template ID (uses default if None)
            include_watermark: Add "BẢN XEM TRƯỚC" watermark

        Returns:
            TemplateResult with HTML content (PDF bytes in real implementation)
        """
        # Render contract with template
        result = self.template_service.render_contract(contract_id, template_id)

        if not result.success:
            return result

        html = result.data['html']

        # Add watermark if preview
        if include_watermark:
            html = self._add_watermark(html, "BẢN XEM TRƯỚC")

        # In real implementation, convert HTML to PDF here
        # For now, return HTML with metadata
        return TemplateResult.ok("PDF generated (HTML format)", {
            'html': html,
            'content_type': 'text/html',
            'filename': f"HD{contract_id:06d}_{datetime.now().strftime('%Y%m%d')}.html",
            'is_preview': include_watermark
        })

    def generate_payment_receipt(
        self,
        payment_id: int,
        contract_id: int = None
    ) -> TemplateResult:
        """Generate payment receipt.

        Args:
            payment_id: Payment ID
            contract_id: Optional contract ID

        Returns:
            TemplateResult
        """
        # In real implementation, get payment details and generate receipt
        # For now, return placeholder
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .receipt {{ border: 2px solid #333; padding: 30px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .amount {{ font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0; }}
                .footer {{ margin-top: 50px; display: flex; justify-content: space-between; }}
            </style>
        </head>
        <body>
            <div class="receipt">
                <div class="header">
                    <h1>PHIẾU THU TIỀN</h1>
                    <p>Mã phiếu: PT{payment_id:06d}</p>
                </div>
                <p>Ngày: {datetime.now().strftime('%d/%m/%Y')}</p>
                <p>Người nộp: _________________________________</p>
                <p>Lý do: Thanh toán hợp đồng</p>
                <div class="amount">
                    Số tiền: _________________________________ VNĐ
                </div>
                <div class="footer">
                    <div>Người lập phiếu</div>
                    <div>Người nộp tiền</div>
                    <div>Thủ quỹ</div>
                </div>
            </div>
        </body>
        </html>
        """

        return TemplateResult.ok("Receipt generated", {
            'html': html,
            'content_type': 'text/html',
            'filename': f"PT{payment_id:06d}_{datetime.now().strftime('%Y%m%d')}.html"
        })

    def generate_contract_summary(
        self,
        contract_ids: List[int],
        start_date: datetime = None,
        end_date: datetime = None
    ) -> TemplateResult:
        """Generate summary report for multiple contracts.

        Args:
            contract_ids: List of contract IDs
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            TemplateResult
        """
        # In real implementation, query contracts and generate summary
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #333; padding: 8px; text-align: left; }}
                th {{ background-color: #f0f0f0; }}
                .summary {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>BÁO CÁO TỔNG HỢP HỢP ĐỒNG</h1>
            <p>Thời gian: {start_date.strftime('%d/%m/%Y') if start_date else '---'}
               đến {end_date.strftime('%d/%m/%Y') if end_date else '---'}</p>

            <div class="summary">
                <p>Tổng số hợp đồng: {len(contract_ids)}</p>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Mã HĐ</th>
                        <th>Khách hàng</th>
                        <th>Xe</th>
                        <th>Giá trị</th>
                        <th>Trạng thái</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td colspan="6" style="text-align: center;">Chi tiết hợp đồng...</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        return TemplateResult.ok("Summary generated", {
            'html': html,
            'content_type': 'text/html',
            'filename': f"contract_summary_{datetime.now().strftime('%Y%m%d')}.html"
        })

    def _add_watermark(self, html: str, watermark_text: str) -> str:
        """Add watermark to HTML.

        Args:
            html: HTML content
            watermark_text: Watermark text

        Returns:
            HTML with watermark
        """
        watermark_style = f"""
        <style>
        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 72px;
            font-weight: bold;
            color: rgba(200, 0, 0, 0.2);
            z-index: 1000;
            pointer-events: none;
        }}
        </style>
        """

        watermark_div = f'<div class="watermark">{watermark_text}</div>'

        # Insert before </body>
        if '</body>' in html:
            html = html.replace('</body>', f'{watermark_div}</body>')
        else:
            html += watermark_div

        # Insert style before </head>
        if '</head>' in html:
            html = html.replace('</head>', f'{watermark_style}</head>')
        else:
            html = f'<head>{watermark_style}</head>' + html

        return html

    def get_print_friendly_html(self, html: str) -> str:
        """Add print-friendly CSS to HTML.

        Args:
            html: HTML content

        Returns:
            Print-friendly HTML
        """
        print_css = """
        <style>
        @media print {
            body { margin: 0; }
            .no-print { display: none !important; }
            .page-break { page-break-before: always; }
        }
        </style>
        """

        if '</head>' in html:
            return html.replace('</head>', f'{print_css}</head>')
        return f'<head>{print_css}</head>{html}'

    def merge_pdfs(self, pdf_contents: List[bytes]) -> bytes:
        """Merge multiple PDFs into one.

        Args:
            pdf_contents: List of PDF bytes

        Returns:
            Merged PDF bytes
        """
        # In real implementation, use PyPDF2 or similar
        # For now, return placeholder
        return b"Merged PDF content placeholder"

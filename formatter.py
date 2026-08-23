def format_text(pris, karat_priser):
    """
    HTML-layout til Guldagent v1.
    Roder ikke med calculator – bruger kun eksisterende nøgler:
    '18kt', '14kt', '8kt'.
    """

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.5;">
        <h2 style="margin-bottom: 0.5rem;">Dagens guldpriser</h2>
        <p style="margin-top: 0;">
          <strong>Finguld:</strong> {pris} kr/gram
        </p>

        <table style="border-collapse: collapse; margin-top: 1rem;">
          <thead>
            <tr>
              <th style="border-bottom: 1px solid #ccc; padding: 4px 8px; text-align: left;">Karat</th>
              <th style="border-bottom: 1px solid #ccc; padding: 4px 8px; text-align: right;">Kundepris (-20%)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="padding: 4px 8px;">18 kt</td>
              <td style="padding: 4px 8px; text-align: right;">
                {karat_priser.get('18kt')} kr
              </td>
            </tr>
            <tr>
              <td style="padding: 4px 8px;">14 kt</td>
              <td style="padding: 4px 8px; text-align: right;">
                {karat_priser.get('14kt')} kr
              </td>
            </tr>
            <tr>
              <td style="padding: 4px 8px;">8 kt</td>
              <td style="padding: 4px 8px; text-align: right;">
                {karat_priser.get('8kt')} kr
              </td>
            </tr>
          </tbody>
        </table>
      </body>
    </html>
    """

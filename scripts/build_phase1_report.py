"""Render Phase-1 PDF from the existing validated CSV/JSON and PNG evidence.

Run from the project root. This presentation script never opens the raw Parquet
and does not change analytical scripts, populations, calculations or outputs.
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
import pandas as pd
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer,
    KeepTogether, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4

with open('outputs/audit_summary.json', encoding='utf-8') as source:
    s = json.load(source)
q = s['quality']
styles = getSampleStyleSheet()
story = []

# ReportLab bundles Vera: no machine-specific fonts or new project assets.
font_dir = next(Path(d) for d in rl_config.TTFSearchPath
                if (Path(d) / 'Vera.ttf').is_file())
for name, filename in [('Vera', 'Vera.ttf'), ('Vera-Bold', 'VeraBd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(font_dir / filename)))

INK = colors.HexColor('#20252B')
ACCENT = colors.HexColor('#294B62')
MUTED = colors.HexColor('#505A64')
RULE = colors.HexColor('#C7CED3')
PALE = colors.HexColor('#F2F5F7')
PAGE_W, PAGE_H = A4
MARGIN = 47
WIDTH = PAGE_W - 2*MARGIN

styles['BodyText'].fontName = 'Times-Roman'
styles['BodyText'].fontSize = 10.2
styles['BodyText'].leading = 13
styles['BodyText'].textColor = INK
styles['BodyText'].spaceBefore = 0
styles['BodyText'].spaceAfter = 6
styles['BodyText'].allowWidows = 0
styles['BodyText'].allowOrphans = 0
styles['Title'].fontName = 'Vera-Bold'
styles['Title'].fontSize = 17
styles['Title'].leading = 21
styles['Title'].alignment = TA_LEFT
styles['Title'].textColor = INK
styles['Title'].spaceAfter = 12
styles['Heading2'].fontName = 'Vera-Bold'
styles['Heading2'].fontSize = 11.2
styles['Heading2'].leading = 15
styles['Heading2'].textColor = ACCENT
styles['Heading2'].spaceBefore = 9
styles['Heading2'].spaceAfter = 6
styles['Heading2'].keepWithNext = True
styles['Italic'].fontName = 'Times-Roman'
styles['Italic'].fontSize = 9.1
styles['Italic'].leading = 11.3
styles['Italic'].textColor = MUTED
styles['Italic'].spaceAfter = 9
styles.add(ParagraphStyle('Small', parent=styles['BodyText'],
                         fontSize=9.3, leading=11.5, spaceAfter=5))
styles.add(ParagraphStyle('Cell', fontName='Times-Roman',
                         fontSize=8.9, leading=10.7, textColor=INK))
styles.add(ParagraphStyle('Number', parent=styles['Cell'], alignment=TA_RIGHT))
styles.add(ParagraphStyle('CellHead', fontName='Vera-Bold',
                         fontSize=8.0, leading=10.2, textColor=INK))

# Only presentation labels are changed; scientific wording is retained below.
HEADINGS = {
    'Problem and decision': '1. Problem and decision',
    'Source and exact population': '2. Source and study population',
    'Structure and quality': '3. Structure, quality and cleaning decisions',
    'Univariate and multivariate evidence': '4. Univariate and multivariate evidence',
    'Temporal and spatial EDA': '5. Temporal patterns',
    'Research design, limitations and ethics': '7. Research design, limitations and ethics',
    'Reproducibility': '8. Reproducibility',
}


def p(text, style='BodyText'):
    text = HEADINGS.get(text, text)
    # Paragraph markup must not interpret comparison operators as HTML.
    text = text.replace('<=', '&lt;=')
    if text.startswith('Rules overlap'):
        text = text.replace(' Raw summaries in', '<br/><br/>Raw summaries in')
        text = text.replace(' Sample correlations', '<br/><br/>Sample correlations')
    if text.startswith('Three questions:'):
        text = text.replace('Three questions:', '<b>Three questions:</b><br/>')
        for number in (1, 2, 3):
            marker = f'({number})'
            text = text.replace(marker, ('<br/>' if number > 1 else '') + '<b>' + marker + '</b>')
        text = text.replace(' Q2 is selected', '<br/><br/>Q2 is selected')
        text = text.replace(' Target for zone', '<br/><br/><b>Target and prediction unit.</b> Target for zone')
        text = text.replace(' Baseline:', '<br/><br/><b>Baseline:</b>')
        text = text.replace(' MAE measures', '<br/><b>Metrics.</b> MAE measures')
    if text.startswith('Proposed future split:'):
        text = text.replace('Proposed future split:', '<b>Proposed future split:</b>')
        text = text.replace(' Only features', '<br/><br/><b>Leakage precautions.</b> Only features')
        text = text.replace(' Future unsupervised', '<br/><br/>Future unsupervised')
    story.append(Paragraph(text, styles[style]))


def table(rows):
    # Fixed widths, wrapped cells and right-aligned counts replace auto-sizing.
    caption = ('Table 1. Source and analysis populations.' if len(rows[0]) == 2
               else 'Table 2. Quality flags across raw records.')
    story.append(Paragraph(caption, styles['Italic']))
    widths = [WIDTH-104, 104] if len(rows[0]) == 2 else [205, 110, WIDTH-315]
    cells = []
    for i, row in enumerate(rows):
        rendered = []
        for j, value in enumerate(row):
            text = str(value)
            if i and j == 1:
                text = re.sub(r'\b\d{4,}\b', lambda m: f'{int(m[0]):,}', text)
            style = 'CellHead' if i == 0 else 'Number' if j == 1 else 'Cell'
            rendered.append(Paragraph(escape(text), styles[style]))
        cells.append(rendered)
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PALE),
        ('LINEABOVE', (0,0), (-1,0), .65, ACCENT),
        ('LINEBELOW', (0,0), (-1,0), .5, ACCENT),
        ('INNERGRID', (0,1), (-1,-1), .2, RULE),
        ('LINEBELOW', (0,-1), (-1,-1), .5, RULE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.extend([t, Spacer(1,7)])


FIGURES = {
    'trip_distributions.png': (1, WIDTH),
    'fare_distance.png': (2, 365),
    'pickup_hour_comparison.png': (3, 380),
    'pickup_date.png': (4, 380),
    'weekday_hour.png': (5, 340),
    'top_pickup_zones.png': (6, 340),
}


def chart(name, caption):
    # Original evidence images remain unchanged and keep their aspect ratio.
    number, width = FIGURES[name]
    item = Image('figures/' + name)
    # Read lazy image dimensions before assigning either display dimension.
    image_width, image_height = item.imageWidth, item.imageHeight
    item.drawWidth = width
    item.drawHeight = width * image_height / image_width
    item.hAlign = 'CENTER'
    label = Paragraph(f'<b>Figure {number}.</b> {caption}', styles['Italic'])
    story.append(KeepTogether([item, label]))


def frame(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont('Vera', 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN, PAGE_H-28, 'NYC TLC Yellow Taxi | Phase 1')
        canvas.drawRightString(PAGE_W-MARGIN, PAGE_H-28, 'January 2024')
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(.4)
        canvas.line(MARGIN, PAGE_H-35, PAGE_W-MARGIN, PAGE_H-35)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.4)
    canvas.line(MARGIN, 36, PAGE_W-MARGIN, 36)
    canvas.setFont('Vera', 7.3)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, 23, 'Data Analysis | Phase 1: problem, data quality and EDA')
    canvas.drawRightString(PAGE_W-MARGIN, 23, str(doc.page))
    canvas.restoreState()


# Five thematic pages keep tables and captions together and avoid stretching
# the supplied figures. The original scientific content is retained verbatim.

p('Phase 1: NYC TLC Yellow Taxi, January 2024','Title')
p('Problem and decision','Heading2')
p('The operational question is whether recent, available trip history can improve next-hour pickup demand forecasts by TLC taxi zone, supporting vehicle allocation. Unit of source data: one provider-submitted trip row. Prediction unit: zone-hour, including future zero-count cells. This observational reporting source covers Yellow Taxi trips, not all NYC mobility.')
p('Source and exact population','Heading2')
p('Official monthly Parquet: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet (49,961,641 bytes). TLC documentation: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page ; dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf . TLC receives vendor submissions and does not guarantee their accuracy or completeness.')
table([['Population','Rows'],['Raw provider rows',f'{s["raw_rows"]:,}'],['Pickup time in [2024-01-01, 2024-02-01)',f'{s["in_scope_pickups"]:,}'],['In month and pickup zone ID 1-263',f'{s["valid_zone_pickups"]:,}'],['Previous trip-quality filtered set, comparison only',f'{s["old_filtered_in_scope"]:,}']])
p(f'There are {q["pickup_outside_january"]} out-of-month pickups ({q["pickup_before_january"]} before January; {q["pickup_after_january"]} in/after February). Minimum timestamp is {s["min_pickup"]}; it is an anomalous record, not evidence of a 2002 study period. An additional {q["jan_outside_study_pu"]:,} in-month rows have pickup zone IDs outside the selected 1-263 study population. Codes 264 (Unknown/N/A) and 265 (Outside of NYC) are recognized special TLC codes, not automatically corrupt identifiers. Counts of demand use all other in-month pickup events regardless of fare, trip duration, or derived speed. No raw rows are deleted. Join the official taxi-zone lookup using PULocationID or DOLocationID against LocationID; the study range also includes Newark Airport and is not exclusively the five NYC boroughs. Membership of every observed code in the official lookup has not been independently checked.')
p('Structure and quality','Heading2')
p(f'The file has {s["source_columns"]} source columns. The full column names, observed dtypes and per-column missing counts/percentages are in outputs/schema_missing.csv. VendorID is a provider code; PULocationID/DOLocationID are zone keys, not unique trip IDs. There is no verified unique trip identifier. Exact duplicates compare every original source column: {q["exact_duplicates"]}; shared time/zone alone is not a duplicate.')
table([['Rule (denominator: raw rows)','Count','Interpretation'],['Missing passenger_count',q['passenger_missing'],'Missing, retain'],['Passenger zero / negative / >6',f'{q["passenger_zero"]} / {q["passenger_negative"]} / {q["passenger_gt_6"]}','Zero/suspicious; inspect, retain for demand'],['Nonpositive duration / reversed time',f'{q["duration_nonpositive"]} / {q["pickup_after_dropoff"]}','Impossible elapsed trip for duration analysis'],['Negative / zero distance',f'{q["distance_negative"]} / {q["distance_zero"]}','Zero may be special trip'],['Negative fare / nonpositive total',f'{q["fare_negative"]} / {q["total_nonpositive"]}','May be corrections/refunds; retain for demand'],['Valid calculated speeds / >80 mph',f'{q["speed_valid_n"]} / {q["speed_gt_80"]}','>80 mph suspicious, not deletion'],['Duration >180 min / distance >50 mi / fare >$200',f'{q["duration_gt_180"]} / {q["distance_gt_50"]} / {q["fare_gt_200"]}','Upper-tail flags, not automatic invalidity'],['Pickup / dropoff outside study range',f'{q["pu_outside_study_range"]} / {q["do_outside_study_range"]}','264/265 are special; see JSON for breakdown']])
story.append(PageBreak())
p('Univariate and multivariate evidence','Heading2')
p('Rules overlap and their counts must not be added. Speed is distance/(duration/60) only for finite nonnegative distance and finite strictly positive duration; otherwise it is missing. The speed-summary denominator is valid calculated speeds, as shown in numeric_summary.csv and the quality table, not all raw rows. Raw summaries in outputs/numeric_summary.csv show medians and IQRs: distance 1.68 mi (1.00-3.11), duration 11.63 min (7.15-18.68), fare $12.80 (8.60-20.50), passengers 1 (1-1). Extreme raw maxima are flagged; the plotted histograms clip display ranges only. Sample correlations (50,000 rows, seed 20261108; positive duration, nonnegative distance/fare, speed <=80): fare-distance '+str(s['sample_fare_distance_corr'])+'; distance-duration '+str(s['sample_distance_duration_corr'])+'. These are associations, not causal effects.')
chart('trip_distributions.png','Trip distance and duration on a reproducible diagnostic sample; clipping affects display only.')
chart('fare_distance.png','Fare-distance joint distribution, 50,000-row diagnostic sample; plotted ranges are limited.')
p('The hourly comparison, weekday-hour heatmap, fare-distance association and zone concentration describe distinct relationships. Full-population count tables and the 50,000-row trip-variable sample have different denominators; their results must not be mixed.')
story.append(PageBreak())
p('Temporal and spatial EDA','Heading2')
p(f'Peak pickup hour is {s["peak_hour"]}:00 ({s["peak_hour_count"]:,} in-month valid-zone submissions). Largest weekday total is {s["peak_weekday"]} ({s["peak_weekday_count"]:,}), influenced by the number of each weekday in January. Largest date is {s["peak_date"]} ({s["peak_date_count"]:,}). See hourly, weekday, daily and weekday-by-hour CSVs. January alone cannot establish annual seasonality.')
chart('pickup_hour_comparison.png','Hourly demand population versus the earlier fare/trip filtered population; the latter undercounts pickup events.')
chart('pickup_date.png','Daily counts for the January valid-zone pickup population.')
story.append(PageBreak())
p('5. Temporal patterns (continued)', 'Heading2')
chart('weekday_hour.png','Weekday-hour joint counts; weekday totals are not normalized by number of occurrences.')
p('6. Spatial distribution and zone imbalance', 'Heading2')
p(f'There are {s["unique_pickup_zones"]} observed pickup zones in the demand population and {s["unique_dropoff_zones"]} observed dropoff zones among January pickup records with dropoff ID 1-263. These are distinct cohorts: dropoff counts do not require a valid pickup zone. The top 10 pickup zones contribute {s["top10_pickup_share_pct"]}% of accepted-zone January pickups; zone {s["top_pickup_zone"]} alone has {s["top_pickup_count"]:,}. Top-10 pickup/dropoff tables contain exact IDs and counts. Missing, zero, official special 264/265 and other out-of-range counts are separated in quality_rules.csv; genuinely unknown lookup keys were not verified. Numeric IDs are not coordinates.')
chart('top_pickup_zones.png','Top 10 pickup zones by count, numeric TLC zone IDs.')
story.append(PageBreak())
p('Research design, limitations and ethics','Heading2')
p('Three questions: (1) How do pickup counts differ by zone, hour and day? (2) Does recent history improve next-hour zone demand forecasting? (3) Which zone-hours differ unusually from historical patterns? Q2 is selected for its direct dispatch relevance and testable baseline. Target for zone z at hour t+1 is the number of pickups within [t+1,t+2); construct a complete zone-hour grid so zero-demand hours appear. Baseline: past same-zone same-hour-of-week average, with past zone mean fallback. MAE measures average count error; RMSLE limits the dominance of high-volume cells (predictions clipped nonnegative).')
p('Proposed future split: train January-October 2024, validation November, test December; impossible to execute with the current January-only file. Only features known before the forecast origin may enter a model; target-hour counts, dropoff, payment and fare must not enter. Aggregates and transformations must be built on earlier periods. Future unsupervised work may cluster zone demand profiles; no model is trained in Phase 1.')
p('Aggregate results to avoid exposing fine-grained mobility. Vendor reporting delays, missing fields, coverage restricted to Yellow Taxi, zone-code validity assumptions and observed outliers constrain generalization. No causal claim follows from observational association. Data-use/licensing claims must follow TLC source terms; a separate blanket license is not asserted.')
p('Reproducibility','Heading2')
p('Run scripts/phase1_eda.py on the named Parquet, then scripts/build_phase1_report.py. outputs/audit_summary.json and CSVs are the numerical source for this report. README and outputs/run_log.txt document commands and environment.')

Path('reports').mkdir(exist_ok=True)
SimpleDocTemplate(
    'reports/phase1.pdf', pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN, topMargin=46, bottomMargin=48,
    title='NYC TLC Yellow Taxi - Phase 1, January 2024',
    subject='Data quality, exploratory analysis and next-hour pickup-demand design',
    author='',
).build(story, onFirstPage=frame, onLaterPages=frame)


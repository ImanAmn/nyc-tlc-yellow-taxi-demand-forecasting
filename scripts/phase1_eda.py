"""Phase 1 TLC audit; run from project root."""
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
SEED=20261108
def main(path):
 o=Path('outputs');f=Path('figures');o.mkdir(exist_ok=True);f.mkdir(exist_ok=True)
 d=pd.read_parquet(path);n=len(d);t=d.tpep_pickup_datetime
 jan=t.ge('2024-01-01')&t.lt('2024-02-01')
 pu=d.PULocationID.notna()&d.PULocationID.between(1,263)
 do=d.DOLocationID.notna()&d.DOLocationID.between(1,263)
 pop=d.loc[jan&pu]; inmonth=d.loc[jan]
 duration=(d.tpep_dropoff_datetime-t).dt.total_seconds()/60
 # Calculated speed is defined only for finite nonnegative distance and
 # finite strictly positive duration. Anomalous rows remain in the raw audit.
 speed_valid=duration.gt(0)&np.isfinite(duration)&d.trip_distance.ge(0)&np.isfinite(d.trip_distance)
 speed=(d.trip_distance/(duration/60)).where(speed_valid).replace([np.inf,-np.inf],np.nan)
 old=jan&pu&duration.gt(0)&d.trip_distance.ge(0)&d.fare_amount.ge(0)&d.total_amount.gt(0)&speed.le(80)
 schema=pd.DataFrame({'column':d.columns,'dtype':d.dtypes.astype(str).values,'missing_n':d.isna().sum().values})
 schema['missing_pct']=schema.missing_n/n*100;schema.to_csv(o/'schema_missing.csv',index=False)
 q={'exact_duplicates':int(d.duplicated().sum()),'pickup_missing':int(t.isna().sum()),'pickup_outside_january':int((~jan&t.notna()).sum()),'pickup_before_january':int(t.lt('2024-01-01').sum()),'pickup_after_january':int(t.ge('2024-02-01').sum()),'pu_missing':int(d.PULocationID.isna().sum()),'pu_zero':int(d.PULocationID.eq(0).sum()),'pu_outside_study_range':int((d.PULocationID.notna()&~pu).sum()),'pu_special_264_unknown':int(d.PULocationID.eq(264).sum()),'pu_special_265_outside_nyc':int(d.PULocationID.eq(265).sum()),'pu_other_outside_1_265':int((d.PULocationID.notna()&~d.PULocationID.between(1,265)).sum()),'do_missing':int(d.DOLocationID.isna().sum()),'do_zero':int(d.DOLocationID.eq(0).sum()),'do_outside_study_range':int((d.DOLocationID.notna()&~do).sum()),'do_special_264_unknown':int(d.DOLocationID.eq(264).sum()),'do_special_265_outside_nyc':int(d.DOLocationID.eq(265).sum()),'do_other_outside_1_265':int((d.DOLocationID.notna()&~d.DOLocationID.between(1,265)).sum()),'jan_outside_study_pu':int((jan&~pu).sum()),'duration_nonpositive':int(duration.le(0).sum()),'pickup_after_dropoff':int(duration.lt(0).sum()),'distance_negative':int(d.trip_distance.lt(0).sum()),'distance_zero':int(d.trip_distance.eq(0).sum()),'fare_negative':int(d.fare_amount.lt(0).sum()),'total_nonpositive':int(d.total_amount.le(0).sum()),'passenger_missing':int(d.passenger_count.isna().sum()),'passenger_zero':int(d.passenger_count.eq(0).sum()),'passenger_negative':int(d.passenger_count.lt(0).sum()),'passenger_gt_6':int(d.passenger_count.gt(6).sum()),'speed_valid_n':int(speed.notna().sum()),'speed_gt_80':int(speed.gt(80).sum()),'duration_gt_180':int(duration.gt(180).sum()),'distance_gt_50':int(d.trip_distance.gt(50).sum()),'fare_gt_200':int(d.fare_amount.gt(200).sum())}
 pd.DataFrame([{'rule':k,'count':v,'pct_raw':v/n*100} for k,v in q.items()]).to_csv(o/'quality_rules.csv',index=False)
 h=pd.DataFrame({'hour':range(24),'all_january':inmonth.groupby(inmonth.tpep_pickup_datetime.dt.hour).size().reindex(range(24),fill_value=0).values,'demand':pop.groupby(pop.tpep_pickup_datetime.dt.hour).size().reindex(range(24),fill_value=0).values,'old_filtered':d.loc[old].groupby(t.loc[old].dt.hour).size().reindex(range(24),fill_value=0).values});h.to_csv(o/'pickup_hour.csv',index=False)
 days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']; w=pop.tpep_pickup_datetime.dt.day_name().value_counts().reindex(days,fill_value=0);w.rename_axis('weekday').reset_index(name='count').to_csv(o/'pickup_weekday.csv',index=False)
 dates=pop.tpep_pickup_datetime.dt.date.value_counts().sort_index();dates.rename_axis('date').reset_index(name='count').to_csv(o/'pickup_date.csv',index=False)
 heat=pd.crosstab(pop.tpep_pickup_datetime.dt.day_name(),pop.tpep_pickup_datetime.dt.hour).reindex(index=days,columns=range(24),fill_value=0);heat.to_csv(o/'weekday_hour.csv')
 a=pop.PULocationID.value_counts();b=d.loc[jan&do,'DOLocationID'].value_counts()
 a.head(10).rename_axis('zone_id').reset_index(name='count').to_csv(o/'top_pickup_zones.csv',index=False);b.head(10).rename_axis('zone_id').reset_index(name='count').to_csv(o/'top_dropoff_zones.csv',index=False)
 num=d[['trip_distance','fare_amount','total_amount','passenger_count']].assign(duration_min=duration,speed_mph=speed.replace([np.inf,-np.inf],np.nan));num.describe(percentiles=[.01,.25,.5,.75,.99]).T.to_csv(o/'numeric_summary.csv')
 good=jan&duration.gt(0)&d.trip_distance.ge(0)&d.fare_amount.ge(0)&speed.le(80);sample=d.loc[good].sample(n=min(50000,int(good.sum())),random_state=SEED).assign(duration_min=duration.loc[good],speed_mph=speed.loc[good]);c=sample[['trip_distance','duration_min','speed_mph','fare_amount']].corr();c.to_csv(o/'trip_correlations_sample.csv')
 s={'raw_rows':n,'source_columns':len(d.columns),'in_scope_pickups':int(jan.sum()),'valid_zone_pickups':len(pop),'old_filtered_in_scope':int(old.sum()),'quality':q,'unique_pickup_zones':len(a),'unique_dropoff_zones':len(b),'top10_pickup_share_pct':round(a.head(10).sum()/len(pop)*100,4),'top_pickup_zone':int(a.index[0]),'top_pickup_count':int(a.iloc[0]),'peak_hour':int(h.loc[h.demand.idxmax(),'hour']),'peak_hour_count':int(h.demand.max()),'peak_weekday':str(w.idxmax()),'peak_weekday_count':int(w.max()),'peak_date':str(dates.idxmax()),'peak_date_count':int(dates.max()),'min_pickup':str(t.min()),'max_pickup':str(t.max()),'sample_fare_distance_corr':round(float(c.loc['fare_amount','trip_distance']),4),'sample_distance_duration_corr':round(float(c.loc['trip_distance','duration_min']),4),'sample_n':len(sample),'seed':SEED}
 (o/'audit_summary.json').write_text(json.dumps(s,indent=2));sns.set_theme(style='whitegrid')
 def save(name): plt.tight_layout();plt.savefig(f/name,dpi=150);plt.close()
 h.plot(x='hour',y=['demand','old_filtered'],title='January pickup counts by hour');plt.ylabel('Submitted records');save('pickup_hour_comparison.png')
 plt.plot(range(len(dates)),dates.values);plt.xticks(range(0,31,5),range(1,32,5));plt.title('January pickup counts by calendar date');plt.xlabel('January day of month');plt.ylabel('Valid-zone pickups');save('pickup_date.png')
 sns.heatmap(heat,cmap='Blues');plt.title('Pickup weekday by hour');save('weekday_hour.png')
 a.head(10).plot.bar(title='Top 10 pickup zone IDs');plt.ylabel('Trips');save('top_pickup_zones.png')
 fig,ax=plt.subplots(1,2,figsize=(10,3));sns.histplot(sample.trip_distance.clip(upper=25),bins=50,ax=ax[0]);sns.histplot(sample.duration_min.clip(upper=90),bins=50,ax=ax[1]);ax[0].set(xlabel='Miles, clipped at 25');ax[1].set(xlabel='Minutes, clipped at 90');save('trip_distributions.png')
 plt.hexbin(sample.trip_distance,sample.fare_amount,gridsize=55,extent=(0,30,0,110),mincnt=1,bins='log');plt.xlabel('Miles');plt.ylabel('Fare ($)');save('fare_distance.png')
 print(json.dumps(s,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);main(p.parse_args().input)

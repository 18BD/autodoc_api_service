from datetime import datetime, timedelta

from celery import shared_task
from logging import getLogger
import pandas as pd

from sales.models import Sale, SaleError


logger = getLogger('django')


@shared_task(bind=True)
def work_with_file(self, sale_id: int):
    status = Sale.Status.FAILURE

    try:
        sale = Sale.objects.get(pk=sale_id)
        if sale.filename.endswith('.csv'):
            status = work_with_csv_file(sale)
        else:
            status = work_with_excel_file(sale)
        
    except Exception as e:
        logger.error(e)
        SaleError.objects.create(sale_id=sale_id, message=str(e))


    sale.status = status
    sale.save(update_fields=['status'])
    
    return None


def work_with_csv_file(sale: Sale) -> int:
    df = pd.read_csv(sale.file)
    if df.empty:
        logger.info(f'{sale.filename} is emty')
        SaleError.objects.create(sale_id=sale.pk, message=f'{sale.filename} is emty')
        return Sale.Status.FAILURE
    
    nan_exists = df['Date'].isnull().values.any()

    if not nan_exists:
        return Sale.Status.SUCCESS

    if nan_exists:
        df = df.where(pd.notnull(df), None)
        last_data = df['Date'].iloc[0]
        for index, row in df.iterrows():
            if not row[0]:
                datetime_object = datetime.strptime(last_data, '%Y-%m-%d')
                datetime_object += timedelta(days=1)
                last_data = datetime_object.strftime('%Y-%m-%d')
                df.at[index, 'Date'] = last_data
            else:
                last_data = row[0]

    df.to_csv(sale.file.path)
    return Sale.Status.SUCCESS


def work_with_excel_file(sale: Sale) -> int:
    df = pd.read_excel(sale.file)
    if df.empty:
        logger.info(f'{sale.filename} is emty')
        SaleError.objects.create(sale_id=sale.pk, message=f'{sale.filename} is emty')
        return Sale.Status.FAILURE
    
    df = df.where(pd.notnull(df), None)
    last_data = df['Date'].iloc[0]

    if pd.isnull(last_data):
        logger.info(f'{sale.filename} start date not exists')
        SaleError.objects.create(sale_id=sale.pk, message=f'{sale.filename} start date not exists')
        return Sale.Status.FAILURE

    for index, row in df.iterrows():
        if pd.isnull(row[0]):
            last_data += timedelta(days=1)
            df.at[index, 'Date'] = last_data
        else:
            last_data = row[0]

    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df.to_excel(sale.file.path, index=False)
    return Sale.Status.SUCCESS


from decimal import Decimal
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from lib.pricing import PriceBook
from lib.costs import window, rows, utc


def book():
    return PriceBook({'lastUpdated':'2026-09-10','items':[
        {'partNumber':part,'currencyCodeLocalizations':[{'currencyCode':'USD','prices':bands}]}
        for part,bands in [('B91628',[{'model':'PAY_AS_YOU_GO','value':0,'rangeMin':0,'rangeMax':10},{'model':'PAY_AS_YOU_GO','value':.0255,'rangeMin':10}]),
                           ('B93030',[{'model':'PAY_AS_YOU_GO','value':0,'rangeMin':0,'rangeMax':744},{'model':'PAY_AS_YOU_GO','value':.0113,'rangeMin':744}]),
                           ('B91961',[{'model':'PAY_AS_YOU_GO','value':.0255}])]]})


@pytest.mark.parametrize('sku,q,rate',[('B91628',100,'.0255'),('B93030',1488,'.0113'),('B91961',100,'.0255'),('B91628',10,'.0255'),('B91628',0,'0')])
def test_marginal_rate(sku,q,rate): assert book().rate(sku,q)==Decimal(rate)


def test_allowance_is_graduated_and_shared():
    b=book()
    assert b.cost('B91628',100)==Decimal('2.295')
    assert b.cost('B93030',1488)==Decimal('8.4072')
    assert b.avoided('B91628',100,20)==Decimal('.51')
    assert b.avoided('B91628',15,10)==Decimal('.1275')


@pytest.mark.parametrize('q',[-1,'NaN','Infinity'])
def test_invalid_quantities(q):
    with pytest.raises(ValueError): book().cost('B91628',q)


def test_monthly_snaps_and_rejects_echo_expansion():
    start,end=window('2026-07-15','2026-09-09','MONTHLY',now=utc('2026-09-10'),delta=True)
    assert (start.day,end.day)==(1,1)
    with pytest.raises(ValueError): rows([{'time-usage-started':'2026-06-01','time-usage-ended':'2026-07-01','computed-amount':1}],start,end)


@pytest.mark.parametrize('start,end,gran,delta',[
    ('2026-09-01','2026-09-02','TOTAL',False),('2026-09-01','2026-09-03','HOURLY',False),
    ('2026-07-01','2026-07-02','HOURLY',False),('2026-09-08','2026-09-09','DAILY',True)])
def test_cost_window_refusals(start,end,gran,delta):
    with pytest.raises(ValueError): window(start,end,gran,now=utc('2026-09-10'),delta=delta)


def test_group_limit_and_currency_streams():
    with pytest.raises(ValueError): window('2026-08-01','2026-09-01','MONTHLY',groups=list('abcde'))
    start,end=window('2026-08-01','2026-09-01','MONTHLY',groups=list('abcd'))
    data=[dict(zip(['time-usage-started','time-usage-ended','computed-amount','currency'],r)) for r in [
        ('2026-08-02','2026-08-03',2,'BRL'),('2026-08-01','2026-08-02',-1,'USD'),('2026-08-01','2026-08-02',0,' ')]]
    out=rows(data,start,end)
    assert [r['currency'] for r in out]==['USD','BRL']


def test_monthly_rejects_partial_bucket():
    with pytest.raises(ValueError):
        rows([{'time-usage-started':'2026-08-15','time-usage-ended':'2026-09-01','computed-amount':1,'currency':'USD'}], utc('2026-08-01'),utc('2026-09-01'),monthly=True)


def test_read_wrapper_retries_only_429(monkeypatch):
    from lib import oci_ro
    from types import SimpleNamespace
    attempts=[]
    sleeps=[]
    def process(*args, **kwargs):
        attempts.append(1)
        return SimpleNamespace(returncode=1,stdout='',stderr='{"status":429,"code":"TooManyRequests"}')
    monkeypatch.setattr(oci_ro,'run_process',process)
    monkeypatch.setattr(oci_ro.time,'sleep',sleeps.append)
    result=oci_ro.run(['compute','instance','list','--compartment-id','placeholder','--limit','1'])
    assert not result['ok'] and len(attempts)==3 and sleeps==[1,2]
    monkeypatch.setattr(oci_ro,'run_process',lambda *a,**kw: SimpleNamespace(returncode=1,stdout='',stderr='{"status":404,"code":"LifecyclePolicyNotFound"}'))
    assert oci_ro.run(['os','object-lifecycle-policy','get','--bucket-name','placeholder'])['error']['code']=='LifecyclePolicyNotFound'

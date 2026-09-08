"""Heuristic inventory labels, not authorization; derived from the audited CLI census."""
import re

READ_PREFIX=re.compile(r"^(list|get|show|describe|head|read|fetch|view|inspect|summarize|summarise|search|query|find|resolve|lookup|preview|estimate|forecast|predict|recommend|suggest|evaluate|compare|diff|count|status|check|verify|analyze|analyse|detect|batch-detect|classify|extract|translate|render|parse|download|chat|embed|rerank|recommendations|tail)(-|_|$)")
DESTRUCTIVE=["delete","cascading-delete","terminate","purge","destroy","remove","detach","deregister","unregister","revoke","disable","deactivate","reset","softreset","stop","reboot","shutdown","cancel","unassign","release","drop","withdraw","abort","evict","rotate","failover","fail-over","switchover","scale-down","close","suspend","restore","expire","disassociate","dissociate","clear","truncate","kill"]
MUTATING=["create","update","change-compartment","move","attach","enable","start","launch","add","assign","import","upload","put","patch","promote","publish","register","install","apply","run","invoke","activate","generate","rename","set","upgrade","downgrade","migrate","clone","copy","export","recover","refresh","resume","validate","test","connect","associate","replace","merge","commit","approve","reject","submit","schedule","trigger","bulk","configure","scale","request","accept","decline","confirm","complete","finalize","initiate","sync","restart","reprovision","recompute","reassign","retry","rerun","backup","snapshot","provision","deploy","transfer","link","unlink","subscribe","unsubscribe","grant","modify","adjust","increase","decrease","swap","rollback","undo","resize","rotate-key"]
def hit(op,v): return op==v or op.startswith(v+"-") or op.endswith("-"+v) or ("-"+v+"-") in op
def classify(op):
    for v in DESTRUCTIVE:
        if hit(op,v): return "destructive",v
    if READ_PREFIX.match(op): return "read",None
    for v in MUTATING:
        if hit(op,v): return "mutating",v
    return "unknown",None
STATEFUL=re.compile(r"^(db|database-management|data-safe|bv|os|fs|kms|vault|secrets|mysql|nosql|opensearch|bds|streaming|queue|recovery|dbmulticloud|distributed-database|distributed-database-v26|psql|redis|blockchain|data-catalog|data-integration|log-analytics|logging|media-services|marketplace-publisher|analytics|goldengate|adb-d|autonomous)\b")
IDENTITY=re.compile(r"^(iam|identity-domains|kms|vault|secrets|certs-mgmt|certificates|bastion|cloud-guard|audit|logging|waas|waf|network-firewall|apiaccesscontrol|access-governance-cp|vulnerability-scanning|delegate-access-control|budgets|usage-api|limits|announce|onboarding|tenant-manager-control-plane|organizations|domains)\b")
NETWORK=re.compile(r"^(network|nlb|lb|dns|vn-monitoring|service-connector|cluster-placement-groups|compute-management|ce|container-instances|compute)\b")
HARD=re.compile(r"(^|-)(purge|destroy|terminate|delete|drop|expire|truncate)(-|$)")
AVAIL=re.compile(r"(^|-)(stop|reboot|shutdown|softreset|reset|detach|disable|deactivate|suspend|failover|fail-over|switchover|release|evict|unassign|scale-down|withdraw|close|abort|cancel|revoke|remove|deregister|unregister|disassociate|dissociate|rotate|restore|clear|kill)(-|$)")
EPHEMERAL=re.compile(r"\b(work-request|job|run|task|report|export|import-request|preview|session|token|command|execution|scan|analysis|assessment|alert|event|test|trace|sample|snapshot-schedule)\b")

def severity(l):
    p=l["path"]; svc=p.split(" ")[0]; op=p.split(" ")[-1]
    if l["kind"]!="destructive": return None
    hard=bool(HARD.search(op))
    if hard:
        if EPHEMERAL.search(p): return "MEDIUM"
        if STATEFUL.match(svc): return "CRITICAL"
        if IDENTITY.match(svc): return "HIGH"
        if NETWORK.match(svc): return "HIGH"
        return "HIGH"
    # availability / access
    if re.search(r"(^|-)(revoke|disable|deactivate|remove|deregister|unregister)(-|$)",op) and IDENTITY.match(svc): return "HIGH"
    if EPHEMERAL.search(p) and re.search(r"(^|-)(cancel|abort|stop|close)(-|$)",op): return "LOW"
    if AVAIL.search(op): return "MEDIUM"
    return "MEDIUM"


READ_EXCEPTIONS = {
    "search resource structured-search", "search resource free-text-search",
    "usage-api usage-summary request-summarized-usages",
    "log-analytics storage estimate-purge-data-size",
    "log-analytics storage estimate-release-data-size",
}

def read_allowed(path):
    op = path.split()[-1]
    return (bool(re.fullmatch(r"(list|get|search|head|summarize|describe)(-[a-z0-9_-]+)?", op))
            or path in READ_EXCEPTIONS)

def annotate(path):
    kind, verb = classify(path.split()[-1])
    level = severity({"path": path, "kind": kind})
    if kind == "mutating":
        level = "MEDIUM" if verb in {"change-compartment", "move", "replace", "migrate", "rollback", "upgrade", "downgrade", "rotate-key", "scale", "patch", "apply", "import", "put", "upload", "set", "configure", "assign", "attach", "enable", "activate", "update"} else "LOW"
    return {"kind": kind, "verb": path.split()[-1], "severity": level or ("REVIEW" if kind == "unknown" else "NONE"), "read_only": read_allowed(path)}

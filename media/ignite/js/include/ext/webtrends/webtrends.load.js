// WebTrends SmartSource Data Collector Tag v10.2.10
// Copyright (c) 2012 Webtrends Inc.  All rights reserved.
// Tag Builder Version: 4.1.0.10
// Created: 2012.05.15
window.webtrendsAsyncInit=function(){
    var dcs=new Webtrends.dcs().init({
        dcsid:"dcs7ggi1tvz5bdbvfb86i75xm_9b9v",
        domain:"statse.webtrendslive.com",
        timezone:-5,
        offsite:true,
        download:true,
        downloadtypes:"xls,doc,pdf,txt,csv,zip,docx,xlsx,rar,gzip",
        onsitedoms:"mozillaignite.org",
        plugins:{
            //hm:{src:"//s.webtrends.com/js/webtrends.hm.js"}
        }
        }).track();
};
(function(){
    var s=document.createElement("script"); s.async=true; s.src="/media/ignite/js/include/ext/webtrends/webtrends.min.js";    
    var s2=document.getElementsByTagName("script")[0]; s2.parentNode.insertBefore(s,s2);
}());

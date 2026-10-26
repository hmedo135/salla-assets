const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1500,height:500},deviceScaleFactor:2});
await p.goto('file://'+process.cwd()+'/banner2.html');await p.waitForTimeout(2500);
await p.screenshot({path:'haraj-banner-hq.png'});await b.close();})();
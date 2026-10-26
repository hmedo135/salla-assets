const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();
for(const [n,w,h] of [['logo',400,400],['ar',1440,240],['en',1440,240]]){const p=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:2});
await p.goto('file://'+process.cwd()+'/'+n+'.html');await p.waitForTimeout(1500);await p.screenshot({path:n+'.png'});}
await b.close();})();

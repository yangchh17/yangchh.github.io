const fs = require('fs');
const path = require('path');

// 读取所有 HTML 文件
const files = fs.readdirSync('.').filter(f => f.endsWith('.html') && f !== 'index.html');

const projects = [];

files.forEach(file => {
  const html = fs.readFileSync(file, 'utf8');
  
  // 提取标题
  const titleMatch = html.match(/<title>(.*?)\|/);
  const title = titleMatch ? titleMatch[1].trim() : '';
  
  // 提取 hero 部分的信息
  const heroMatch = html.match(/<div class="hero[^"]*"[^>]*>([\s\S]*?)<div style="height:1px/);
  
  let eyebrow = '';
  let systemLine = '';
  let summary = '';
  
  if (heroMatch) {
    const heroContent = heroMatch[1];
    
    // 提取 eyebrow (项目编号和类型)
    const eyebrowMatch = heroContent.match(/<div class="hero-eyebrow">(.*?)<\/div>/);
    eyebrow = eyebrowMatch ? eyebrowMatch[1].replace(/<[^>]*>/g, '').trim() : '';
    
    // 提取 system-line (副标题)
    const systemMatch = heroContent.match(/<div class="hero-system-line">(.*?)<\/div>/);
    systemLine = systemMatch ? systemMatch[1].replace(/<[^>]*>/g, '').trim() : '';
    
    // 提取 summary (描述)
    const summaryMatch = heroContent.match(/<p class="hero-summary">([\s\S]*?)<\/p>/);
    summary = summaryMatch ? summaryMatch[1].replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim() : '';
  }
  
  // 提取 metrics
  const metrics = [];
  const metricsSection = html.match(/<div class="metrics">([\s\S]*?)<\/div>\s*<\/div>\s*<div style="height:1px/);
  if (metricsSection) {
    const metricItems = metricsSection[1].matchAll(/<div class="metric"><div class="metric-val">(.*?)<\/div><div class="metric-label">(.*?)<\/div><\/div>/g);
    for (const match of metricItems) {
      metrics.push({
        value: match[1].trim(),
        label: match[2].trim()
      });
    }
  }
  
  projects.push({
    file,
    title,
    eyebrow,
    systemLine,
    summary,
    metrics
  });
});

// 输出 JSON
console.log(JSON.stringify(projects, null, 2));

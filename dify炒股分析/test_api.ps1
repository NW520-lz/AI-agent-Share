# PowerShell脚本测试API
Write-Host "🔍 测试股票分析HTTP API..." -ForegroundColor Green
Write-Host "=" * 50

$baseUrl = "http://10.7.139.26:8003"

# 1. 测试健康检查
Write-Host "1. 测试健康检查:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 10
    Write-Host "   ✅ 健康检查通过" -ForegroundColor Green
    Write-Host "   响应: $($response | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ 健康检查失败: $($_.Exception.Message)" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "=" * 50

# 2. 测试股票基本信息
Write-Host "2. 测试股票基本信息 (600132):" -ForegroundColor Yellow
try {
    $body = @{
        stock_code = "600132"
        market_type = "A"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$baseUrl/stock-info" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($response.status -eq "success") {
        $stockInfo = $response.data.stock_info
        Write-Host "   ✅ 股票信息获取成功" -ForegroundColor Green
        Write-Host "   股票名称: $($stockInfo.name)" -ForegroundColor Cyan
        Write-Host "   当前价格: $($stockInfo.current_price)" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ API返回错误: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 50

# 3. 测试市场状态
Write-Host "3. 测试市场状态:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/market-status" -Method Get -TimeoutSec 10
    
    if ($response.status -eq "success") {
        $marketStatus = $response.data.market_status
        Write-Host "   ✅ 市场状态获取成功" -ForegroundColor Green
        Write-Host "   市场状态: $($marketStatus.market_status)" -ForegroundColor Cyan
        Write-Host "   当前时间: $($marketStatus.current_time)" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ API返回错误: $($response.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=" * 50

# 4. 测试综合分析
Write-Host "4. 测试综合股票分析 (600132):" -ForegroundColor Yellow
Write-Host "   ⏳ 正在获取数据和分析，请稍候..." -ForegroundColor Yellow

try {
    $body = @{
        stock_code = "600132"
        market_type = "A"
        period = "30"
    } | ConvertTo-Json

    $startTime = Get-Date
    $response = Invoke-RestMethod -Uri "$baseUrl/analyze-stock" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds

    Write-Host "   耗时: $([math]::Round($duration, 2))秒" -ForegroundColor Cyan
    
    if ($response.status -eq "success") {
        $analysisData = $response.data
        $stockInfo = $analysisData.stock_info
        $technical = $analysisData.technical_summary
        
        Write-Host "   ✅ 综合分析成功" -ForegroundColor Green
        Write-Host "   股票名称: $($stockInfo.name)" -ForegroundColor Cyan
        Write-Host "   当前价格: $($stockInfo.current_price)" -ForegroundColor Cyan
        Write-Host "   趋势: $($technical.trend)" -ForegroundColor Cyan
        Write-Host "   RSI: $($technical.rsi)" -ForegroundColor Cyan
        
        # 保存完整响应
        $response | ConvertTo-Json -Depth 10 | Out-File -FilePath "api_response_sample.json" -Encoding UTF8
        Write-Host "   📄 完整响应已保存到 api_response_sample.json" -ForegroundColor Green
        
    } else {
        Write-Host "   ❌ API返回错误: $($response.error)" -ForegroundColor Red
    }
} catch {
    if ($_.Exception.Message -like "*timeout*") {
        Write-Host "   ⏰ 请求超时，这可能是因为数据获取需要较长时间" -ForegroundColor Yellow
        Write-Host "   💡 建议: 在Dify中设置更长的超时时间（60-120秒）" -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ 请求失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=" * 50
Write-Host "🎯 API测试完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Dify配置建议:" -ForegroundColor Yellow
Write-Host "   - HTTP请求超时设置: 60-120秒"
Write-Host "   - URL: http://10.7.139.26:8003/analyze-stock"
Write-Host "   - 方法: POST"
Write-Host "   - Content-Type: application/json"
Write-Host "   - 请求体: {`"stock_code`": `"{{#stock_code#}}`", `"market_type`": `"A`", `"period`": `"30`"}"

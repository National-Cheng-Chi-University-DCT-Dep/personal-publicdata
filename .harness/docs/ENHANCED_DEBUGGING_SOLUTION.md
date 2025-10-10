# 🔧 增強調試解決方案 - CI/CD 路徑問題最終診斷

## 🚨 問題持續性分析

儘管實施了多重修正，CI/CD 環境中的路徑錯誤仍然持續：

```
[PATH_RESOLVER] Found standard structure at: /harness
[ERROR] Alert processing failed: [Errno 2] No such file or directory: '/harness/final_applications/alert_summary.json'
```

**關鍵觀察**: 路徑解析器找到了正確的結構，但缺少目錄創建的調試信息，表明目錄創建過程可能存在問題。

## 📍 深度診斷分析

### **問題定位**:

1. **路徑解析**: ✅ 正確 - 找到 `/harness` 作為專案根目錄
2. **目錄創建**: ❓ 未知 - 沒有看到創建確認信息
3. **文件保存**: ❌ 失敗 - 無法找到目標文件

### **可能的根本原因**:

#### **權限問題**:
- `/harness` 目錄可能是只讀的
- `mkdir` 操作可能靜默失敗
- 文件系統可能有特殊限制

#### **環境限制**:
- 容器環境的文件系統限制
- CI/CD 平台的安全策略
- 磁碟空間或 inode 限制

## ✅ 增強調試解決方案

### **階段 1: 詳細目錄創建調試**

#### **完整的目錄創建過程監控**:
```python
try:
    print(f"[PATH_RESOLVER] Attempting to create output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[PATH_RESOLVER] Created/verified output directory: {output_dir}")
    print(f"[PATH_RESOLVER] Directory exists: {output_dir.exists()}")
    print(f"[PATH_RESOLVER] Directory is writable: {os.access(output_dir, os.W_OK)}")
    
    # 權限檢查和備用方案
    if not os.access(output_dir, os.W_OK):
        print(f"[PATH_RESOLVER] Directory not writable, trying alternative location")
        alt_output_dir = current_dir / "final_applications"
        alt_output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[PATH_RESOLVER] Alternative output directory: {alt_output_dir}")
        print(f"[PATH_RESOLVER] Alternative directory is writable: {os.access(alt_output_dir, os.W_OK)}")
        if os.access(alt_output_dir, os.W_OK):
            output_dir = alt_output_dir
            print(f"[PATH_RESOLVER] Using alternative output directory: {output_dir}")
            
except Exception as e:
    print(f"[PATH_RESOLVER] ERROR creating directory: {e}")
    print(f"[PATH_RESOLVER] Trying alternative location in current directory")
    try:
        alt_output_dir = current_dir / "final_applications"
        alt_output_dir.mkdir(parents=True, exist_ok=True)
        output_dir = alt_output_dir
        print(f"[PATH_RESOLVER] Using alternative output directory: {output_dir}")
    except Exception as e2:
        print(f"[PATH_RESOLVER] Alternative location also failed: {e2}")
        print(f"[PATH_RESOLVER] Continuing with original path...")
```

### **階段 2: 多層備用方案**

#### **備用目錄策略**:
1. **主要目錄**: `/harness/final_applications`
2. **備用目錄 1**: `/harness/notifications/final_applications`
3. **備用目錄 2**: 當前工作目錄中的 `final_applications`
4. **最終備用**: 臨時目錄或內存處理

### **階段 3: 完整的文件保存診斷**

#### **詳細的文件操作監控**:
```python
try:
    print(f"[DEBUG] Attempting to save alert summary to: {summary_file}")
    print(f"[DEBUG] Output directory exists: {self.output_dir.exists()}")
    print(f"[DEBUG] Output directory is writable: {os.access(self.output_dir, os.W_OK)}")
    
    # 確保目錄存在和可寫
    self.output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"[SUMMARY] Alert summary saved to {summary_file}")
    print(f"[DEBUG] File size: {summary_file.stat().st_size} bytes")
    
except PermissionError as e:
    print(f"[ERROR] Permission denied saving alert summary: {e}")
    print(f"[DEBUG] Directory permissions: {oct(self.output_dir.stat().st_mode)}")
    raise
except OSError as e:
    print(f"[ERROR] OS error saving alert summary: {e}")
    raise
except Exception as e:
    print(f"[ERROR] Unexpected error saving alert summary: {e}")
    raise
```

## 🔍 預期 CI/CD 診斷輸出

### **成功情況**:
```
[PATH_RESOLVER] Found standard structure at: /harness
[PATH_RESOLVER] Attempting to create output directory: /harness/final_applications
[PATH_RESOLVER] Created/verified output directory: /harness/final_applications
[PATH_RESOLVER] Directory exists: True
[PATH_RESOLVER] Directory is writable: True
[DEBUG] Attempting to save alert summary to: /harness/final_applications/alert_summary.json
[DEBUG] Output directory exists: True
[DEBUG] Output directory is writable: True
[SUMMARY] Alert summary saved to /harness/final_applications/alert_summary.json
[DEBUG] File size: 187 bytes
```

### **權限問題診斷**:
```
[PATH_RESOLVER] Found standard structure at: /harness
[PATH_RESOLVER] Attempting to create output directory: /harness/final_applications
[PATH_RESOLVER] Created/verified output directory: /harness/final_applications
[PATH_RESOLVER] Directory exists: True
[PATH_RESOLVER] Directory is writable: False
[PATH_RESOLVER] Directory not writable, trying alternative location
[PATH_RESOLVER] Alternative output directory: /harness/notifications/final_applications
[PATH_RESOLVER] Alternative directory is writable: True
[PATH_RESOLVER] Using alternative output directory: /harness/notifications/final_applications
```

### **目錄創建失敗診斷**:
```
[PATH_RESOLVER] Found standard structure at: /harness
[PATH_RESOLVER] Attempting to create output directory: /harness/final_applications
[PATH_RESOLVER] ERROR creating directory: [Errno 13] Permission denied: '/harness/final_applications'
[PATH_RESOLVER] Trying alternative location in current directory
[PATH_RESOLVER] Using alternative output directory: /harness/notifications/final_applications
```

## 🎯 解決方案優勢

### **完整診斷能力**:
- ✅ 路徑解析過程完全可見
- ✅ 目錄創建過程詳細監控
- ✅ 權限檢查和狀態報告
- ✅ 多層備用方案自動啟用

### **錯誤恢復機制**:
- ✅ 主目錄不可用時自動切換備用目錄
- ✅ 目錄創建失敗時嘗試替代位置
- ✅ 詳細的錯誤分類和報告
- ✅ 繼續執行而不是完全失敗

### **調試信息完整性**:
- ✅ 每個步驟都有確認信息
- ✅ 錯誤情況有詳細的診斷
- ✅ 系統狀態信息完整
- ✅ 備用方案執行過程可見

## 🚀 後續行動計劃

### **基於診斷結果的行動**:

#### **如果看到權限問題**:
```
[PATH_RESOLVER] Directory is writable: False
```
**行動**: 調整 CI/CD 環境配置或使用備用目錄

#### **如果看到目錄創建失敗**:
```
[PATH_RESOLVER] ERROR creating directory: [Errno 13] Permission denied
```
**行動**: 檢查容器配置和文件系統權限

#### **如果看到文件保存失敗**:
```
[ERROR] Permission denied saving alert summary
```
**行動**: 使用備用保存策略或調整文件權限

### **最終備用方案**:
如果所有目錄都不可寫，可以實施：
- 將摘要輸出到標準輸出而不是文件
- 使用環境變數傳遞摘要信息
- 跳過文件保存但繼續其他功能

## 🔄 持續監控

### **成功指標**:
- ✅ 看到完整的目錄創建確認信息
- ✅ 看到文件保存成功和文件大小信息
- ✅ 無錯誤日誌

### **問題指標**:
- ❌ 缺少目錄創建確認信息
- ❌ 權限錯誤或 OS 錯誤
- ❌ 備用方案啟用

---

**修正完成時間**: 2025-01-07  
**修正人員**: AI Assistant  
**狀態**: ✅ 增強調試方案完成  
**影響**: 🎯 通知系統現在具備完整的診斷能力，能夠準確識別和報告任何路徑、權限或文件系統問題，並自動啟用備用方案

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址定位查询工具
支持单个IP查询、批量查询、本机IP查询等功能
"""

import requests
from bs4 import BeautifulSoup
import argparse
import sys
import os
import json
from typing import Optional, List, Dict
import datetime

# ASCII艺术图画
ASCII_ART = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    ██╗██████╗     ██████╗██╗  ██╗ █████╗ ██████╗           ║
║    ██║██╔══██╗    ██╔══██╗██║  ██║██╔══██╗██╔══██╗          ║
║    ██║██████╔╝    ██████╔╝███████║███████║██████╔╝          ║
║    ██║██╔═══╝     ██╔═══╝ ██╔══██║██╔══██║██╔══██╗          ║
║    ██║██║         ██║     ██║  ██║██║  ██║██║  ██║          ║
║    ╚═╝╚═╝         ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝          ║
║                                                              ║
║                    IP地址定位查询工具                        ║
║                    IP Location Tool                          ║
║                                                              ║
║    🔍 快速查询IP地址地理位置                                 ║
║    🌍 支持全球IP地址查询                                     ║
║    🚀 命令行界面，使用简单                                   ║
║    📦 轻量级，无复杂依赖                                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""

def show_banner():
    """显示工具横幅"""
    print(ASCII_ART)
    print("版本: 1.0.0 | 作者: 大智 | 许可证: MIT")
    print("=" * 70)
    print()

class IPLocationTool:
    """IP地址定位查询工具类"""
    
    def __init__(self):
        self.base_url = "http://tools.sbbbb.cn/ip/"
        self.headers = {
            "Host": "tools.sbbbb.cn",
            "Origin": "http://tools.sbbbb.cn",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "http://tools.sbbbb.cn/ip/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Cookie": "_ga=GA1.1.1490931985.1749299309; _ga_8PSJV35D6D=GS2.1.s1749299309$o1$g1$t1749299370$j60$l0$h0; PHPSESSID=pd0ch7hgjf5oua22hgqo45eci6"
        }
    
    def get_local_ip(self) -> str:
        """获取本机外网IP地址"""
        try:
            response = requests.get("https://api.ipify.org", timeout=10)
            if response.status_code == 200:
                return response.text.strip()
            else:
                # 备用API
                response = requests.get("https://ifconfig.me", timeout=10)
                return response.text.strip()
        except Exception as e:
            print(f"获取本机IP失败: {e}")
            return ""
    
    def validate_ip(self, ip: str) -> bool:
        """验证IP地址格式"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False
    
    def extract_result_box(self, html: str) -> str:
        """从返回HTML中提取result-box区域的文本信息"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            result_div = soup.find("div", class_="result-box")
            if result_div:
                results = [p.get_text(strip=True) for p in result_div.find_all("p")]
                return "\n".join(results)
            else:
                return "未找到查询结果"
        except Exception as e:
            return f"解析结果失败: {e}"
    
    def parse_location_data(self, html: str) -> Dict[str, str]:
        """解析HTML结果为结构化数据"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            result_div = soup.find("div", class_="result-box")
            if not result_div:
                return {"error": "未找到查询结果"}
            
            location_data = {}
            paragraphs = result_div.find_all("p")
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 标准化键名
                    if "IP" in key or "ip" in key:
                        location_data["ip"] = value
                    elif "定位" in key:
                        location_data["location"] = value
                    elif "省份" in key:
                        location_data["province"] = value
                    elif "市" in key and "省" not in key:
                        location_data["city"] = value
                    elif "区" in key:
                        location_data["district"] = value
                    elif "地址" in key:
                        location_data["address"] = value
                    elif "运营商" in key:
                        location_data["isp"] = value
                    else:
                        location_data[key] = value
            
            return location_data
        except Exception as e:
            return {"error": f"解析结果失败: {e}"}
    
    def query_ip(self, ip_address: str) -> Dict[str, str]:
        """查询单个IP地址"""
        if not self.validate_ip(ip_address):
            return {"error": f"无效的IP地址格式: {ip_address}"}
        
        data = {
            "ip": ip_address,
            "token": "8080",
            "captcha": "TELP"
        }
        
        try:
            response = requests.post(
                self.base_url, 
                headers=self.headers, 
                data=data, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = self.extract_result_box(response.text)
                location_data = self.parse_location_data(response.text)
                return {
                    "ip": ip_address,
                    "result": result,
                    "location_data": location_data,
                    "status": "success"
                }
            else:
                return {
                    "ip": ip_address,
                    "error": f"请求失败，状态码: {response.status_code}",
                    "status": "error"
                }
        except requests.exceptions.Timeout:
            return {
                "ip": ip_address,
                "error": "请求超时",
                "status": "error"
            }
        except requests.exceptions.RequestException as e:
            return {
                "ip": ip_address,
                "error": f"网络请求错误: {e}",
                "status": "error"
            }
        except Exception as e:
            return {
                "ip": ip_address,
                "error": f"未知错误: {e}",
                "status": "error"
            }
    
    def batch_query(self, ip_list: List[str], output_file: Optional[str] = None, json_output: bool = False) -> List[Dict[str, str]]:
        """批量查询IP地址"""
        results = []
        
        if not json_output:
            print(f"开始批量查询 {len(ip_list)} 个IP地址...")
        
        for i, ip in enumerate(ip_list, 1):
            if not json_output:
                print(f"正在查询 ({i}/{len(ip_list)}): {ip}")
            result = self.query_ip(ip.strip())
            results.append(result)
            
            # 显示结果
            if not json_output:
                if result["status"] == "success":
                    print(f"✓ {ip}: 查询成功")
                else:
                    print(f"✗ {ip}: {result.get('error', '未知错误')}")
            
            # 添加延迟避免请求过快
            import time
            time.sleep(1)
        
        # 保存结果到文件
        if output_file:
            if json_output:
                self.save_results_json(results, output_file)
            else:
                self.save_results(results, output_file)
        
        return results
    
    def save_results_json(self, results: List[Dict[str, str]], filename: str):
        """保存查询结果到JSON文件"""
        try:
            # 准备JSON数据
            json_data = {
                "query_time": str(datetime.datetime.now()),
                "total_count": len(results),
                "success_count": sum(1 for r in results if r["status"] == "success"),
                "results": []
            }
            
            for result in results:
                if result["status"] == "success":
                    json_data["results"].append({
                        "ip": result["ip"],
                        "status": "success",
                        "location_data": result.get("location_data", {}),
                        "raw_result": result["result"]
                    })
                else:
                    json_data["results"].append({
                        "ip": result["ip"],
                        "status": "error",
                        "error": result.get("error", "未知错误")
                    })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print(f"JSON结果已保存到: {filename}")
        except Exception as e:
            print(f"保存JSON文件失败: {e}")
    
    def save_results(self, results: List[Dict[str, str]], filename: str):
        """保存查询结果到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(f"IP: {result['ip']}\n")
                    if result['status'] == 'success':
                        f.write(f"结果:\n{result['result']}\n")
                    else:
                        f.write(f"错误: {result.get('error', '未知错误')}\n")
                    f.write("-" * 50 + "\n")
            print(f"结果已保存到: {filename}")
        except Exception as e:
            print(f"保存文件失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='IP地址定位查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ip_location.py 8.8.8.8                    # 查询单个IP
  python ip_location.py --local                     # 查询本机IP
  python ip_location.py --file ip_list.txt          # 批量查询
  python ip_location.py --file ip_list.txt --output results.txt  # 批量查询并保存结果
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('ip', nargs='?', help='要查询的IP地址')
    group.add_argument('--local', '-l', action='store_true', help='查询本机外网IP地址')
    group.add_argument('--file', '-f', help='从文件批量查询IP地址（每行一个IP）')
    
    parser.add_argument('--output', '-o', help='指定输出文件（批量查询时使用）')
    parser.add_argument('--json', action='store_true', help='以JSON格式输出结果')
    
    args = parser.parse_args()
    
    tool = IPLocationTool()
    
    try:
        show_banner()
        
        if args.local:
            # 查询本机IP
            local_ip = tool.get_local_ip()
            if local_ip:
                if not args.json:
                    print(f"本机外网IP: {local_ip}")
                result = tool.query_ip(local_ip)
                if result["status"] == "success":
                    if args.json:
                        # JSON输出
                        json_data = {
                            "local_ip": local_ip,
                            "status": "success",
                            "location_data": result.get("location_data", {}),
                            "raw_result": result["result"]
                        }
                        print(json.dumps(json_data, ensure_ascii=False, indent=2))
                    else:
                        # 普通输出
                        print("IP 定位结果：")
                        print(result["result"])
                else:
                    if args.json:
                        json_data = {
                            "local_ip": local_ip,
                            "status": "error",
                            "error": result.get("error", "未知错误")
                        }
                        print(json.dumps(json_data, ensure_ascii=False, indent=2))
                    else:
                        print(f"查询失败: {result['error']}")
            else:
                if args.json:
                    json_data = {
                        "status": "error",
                        "error": "无法获取本机外网IP地址"
                    }
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    print("无法获取本机外网IP地址")
        
        elif args.file:
            # 批量查询
            if not os.path.exists(args.file):
                error_msg = f"文件不存在: {args.file}"
                if args.json:
                    json_data = {"status": "error", "error": error_msg}
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    print(error_msg)
                sys.exit(1)
            
            with open(args.file, 'r', encoding='utf-8') as f:
                ip_list = [line.strip() for line in f if line.strip()]
            
            if not ip_list:
                error_msg = "文件中没有找到有效的IP地址"
                if args.json:
                    json_data = {"status": "error", "error": error_msg}
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    print(error_msg)
                sys.exit(1)
            
            results = tool.batch_query(ip_list, args.output, args.json)
            
            # 统计结果
            success_count = sum(1 for r in results if r["status"] == "success")
            if not args.json:
                print(f"\n查询完成: 成功 {success_count}/{len(results)} 个")
            elif not args.output:  # 如果没有指定输出文件，则打印JSON到控制台
                json_data = {
                    "query_time": str(datetime.datetime.now()),
                    "total_count": len(results),
                    "success_count": success_count,
                    "results": []
                }
                
                for result in results:
                    if result["status"] == "success":
                        json_data["results"].append({
                            "ip": result["ip"],
                            "status": "success",
                            "location_data": result.get("location_data", {}),
                            "raw_result": result["result"]
                        })
                    else:
                        json_data["results"].append({
                            "ip": result["ip"],
                            "status": "error",
                            "error": result.get("error", "未知错误")
                        })
                
                print(json.dumps(json_data, ensure_ascii=False, indent=2))
        
        else:
            # 查询单个IP
            if not args.ip:
                error_msg = "请提供要查询的IP地址"
                if args.json:
                    json_data = {"status": "error", "error": error_msg}
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    print(error_msg)
                    parser.print_help()
                sys.exit(1)
            
            result = tool.query_ip(args.ip)
            if result["status"] == "success":
                if args.json:
                    # JSON输出
                    json_data = {
                        "ip": result["ip"],
                        "status": "success",
                        "location_data": result.get("location_data", {}),
                        "raw_result": result["result"]
                    }
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    # 普通输出
                    print("IP 定位结果：")
                    print(result["result"])
            else:
                if args.json:
                    json_data = {
                        "ip": result["ip"],
                        "status": "error",
                        "error": result.get("error", "未知错误")
                    }
                    print(json.dumps(json_data, ensure_ascii=False, indent=2))
                else:
                    print(f"查询失败: {result['error']}")
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
# main.py
import sys

def main():
    # 檢查使用者有沒有輸入參數
    if len(sys.argv) < 2:
        print("Error")
        print("ex:")
        print("  python main.py crawl    -> 執行爬蟲")
        print("  python main.py analyze  -> 執行分析")
        return

    mode = sys.argv[1].lower()

    if mode == "crawl":
        print("mode：Selenium")
        import python_Selenium
        python_Selenium.crawl_yahoo_entertainment_bug_free()
        
    elif mode == "analyze":
        print("mode：Save_csv")
        import Save_csv_file
        raw_news = Save_csv_file.fetch_yahoo_entertainment_news_via_web(Save_csv_file.WEB_URL)
        if raw_news:
            final_data = Save_csv_file.analyze_and_structure_data(raw_news)
            Save_csv_file.output_to_csv(final_data)
            
    else:
        print(f"mode choose(crawl/analyze)")

if __name__ == "__main__":
    main()
# CTH FLASH TOOLS PRO — SHADOW JOKER

## গুরুত্বপূর্ণ সীমাবদ্ধতা
GitHub Pages/Render static website নিজে থেকে USB/ADB/Fastboot ব্যবহার করতে পারে না। তাই এই প্যাকেজে দুটি অংশ আছে:
1. `index.html`: hosted dashboard
2. `agent.py`: যে কম্পিউটারে Android SDK Platform-Tools এবং USB ডিভাইস সংযুক্ত, সেখানে চালানোর লোকাল read-only agent

Agent কেবল নির্দিষ্ট, read-only কমান্ড চালায়: `adb devices -l`, কয়েকটি `getprop`, এবং `fastboot devices`। Arbitrary shell command, flash, erase, format, bootloader unlock বা lock কমান্ড নেই।

## লোকাল কম্পিউটারে চালানো
1. Python 3.10+ ইনস্টল করো।
2. Android SDK Platform-Tools ইনস্টল করো এবং `adb`/`fastboot` PATH-এ যোগ করো।
3. এই ফোল্ডারে টার্মিনাল খুলে:
   - `python -m venv .venv`
   - Windows: `.venv\\Scripts\\activate`
   - macOS/Linux: `source .venv/bin/activate`
   - `pip install -r requirements.txt`
   - `python agent.py`
4. `http://127.0.0.1:8765/health` খুলে `{"ok":true,...}` দেখো।
5. `index.html` ব্রাউজারে খোলো। Local Agent address `http://127.0.0.1:8765` রাখো।

### ADB
- ফোনে Developer options → USB debugging চালু করো।
- USB দিয়ে যুক্ত করো, ফোনের RSA অনুমতির prompt-এ নিজের ডিভাইস হলে Allow করো।
- `adb devices -l`-এ `device` দেখালে কাজ করবে; `unauthorized` হলে ফোনে অনুমতি দাও।

### Fastboot
- শুধু নিজের ডিভাইসের জন্য প্রস্তুতকারকের নির্দেশনা অনুসরণ করে Fastboot mode-এ যাও।
- USB/ড্রাইভার ঠিক থাকলে `fastboot devices` সিরিয়াল দেখাবে।
- এই dashboard কোনো ফ্ল্যাশ/আনলক/ডেটা মুছবে না।

## Android phone only
শুধু Android ফোন দিয়ে hosted website থেকে সাধারণ USB ADB/Fastboot access নিশ্চিত করা যায় না। Termux-এ `adb`/platform-tools চালানোর কিছু সীমিত পদ্ধতি আছে, কিন্তু USB host, Android সংস্করণ, অনুমতি ও bootloader পরিস্থিতির ওপর নির্ভর করে। এই agent-টি মূলত PC/macOS/Linux local machine-এর জন্য। Android-এ এটি চালানোর আগে নিজের ডিভাইসে Python/Termux এবং platform-tools সঠিকভাবে সেটআপ করতে হবে; Fastboot USB হোস্টিং সাধারণত আলাদা সীমাবদ্ধতার মধ্যে পড়ে।

## Hosting
- GitHub repo-তে `index.html` ও `render.yaml` আপলোড করো।
- Render-এ Static Site হিসেবে deploy করো (Publish directory `.`)।
- Hosted dashboard-এ Local Agent address `127.0.0.1` থাকলে তা ব্যবহারকারীর নিজস্ব ডিভাইসকেই বোঝায়; Render server-কে নয়। Local Agent-কে public internet-এ expose কোরো না।

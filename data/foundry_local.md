# Microsoft Foundry Local

Foundry Local, yapay zeka modellerini tamamen kullanıcının cihazında çalıştıran bir
yerel çalışma zamanıdır. Azure aboneliği veya sürekli internet bağlantısı gerektirmez;
modeller bir kez indirildikten sonra çevrimdışı çalışır.

Foundry Local, ONNX Runtime üzerine kuruludur ve CPU, GPU ile NPU üzerinde otomatik
donanım hızlandırması sağlar. Windows tarafında Windows ML ile entegre çalışır; macOS
tarafında Apple Silicon GPU üzerinde Metal ile çalışır.

Foundry Local yalnızca Apple Silicon işlemcili Mac'leri destekler. Intel işlemcili
Mac'lerde çalışmaz.

Modeller bir katalogdan alias ile seçilir. Foundry Local, kullanıcının donanımına en
uygun model varyantını otomatik olarak indirir.

# RAG (Retrieval-Augmented Generation) Nedir?

RAG, bir dil modelinin cevaplarını harici bir belge kümesinden alınan bilgiyle
zenginleştiren bir tasarım desenidir. Üç adımdan oluşur: Getirme (Retrieve),
Zenginleştirme (Augment) ve Üretme (Generate).

Önce kullanıcının sorusuna en alakalı belge parçaları bulunur. Ardından bu parçalar
modelin istemine bağlam olarak eklenir. Son olarak model, bu bağlama dayanarak cevabı
üretir.

RAG'in en önemli faydası, cevapların kendi verilerinize dayanması ve böylece
halüsinasyonun azalmasıdır. Ayrıca cevaplarda kaynak gösterilmesini mümkün kılar.

## RAG Ne Zaman Kullanılır?

RAG, bir dil modelinin eğitim verisinde bulunmayan özel belgelere dayalı sorular
cevaplaması gerektiğinde tercih edilir. Örneğin; şirket içi dokümanlar, ders notları,
teknik kılavuzlar veya SSS sayfaları.

## Halüsinasyon Nedir?

Halüsinasyon, bir dil modelinin doğru bilgiye sahip olmadığı halde makul görünen ancak
yanlış cevaplar üretmesidir. RAG bu sorunu, modele yalnızca güvenilir belgelerden
alınan bağlamı vererek azaltır.

## Bu Projede RAG Nasıl Çalışır?

1. Belge parçaları ingest.py ile embedding'e dönüştürülüp rag.db'ye kaydedilir.
2. Kullanıcının sorusu da embedding'e dönüştürülür.
3. retrieval.py, cosine similarity ile en alakalı 3 parçayı bulur.
4. generation.py bu parçaları prompt'a ekler ve yerel chat modelinden cevap alır.
5. Cevap, kaynakları (dosya adları) ile birlikte kullanıcıya döndürülür.

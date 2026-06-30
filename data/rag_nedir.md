# RAG (Retrieval-Augmented Generation) Nedir?

RAG, bir dil modelinin cevaplarını harici bir belge kümesinden alınan bilgiyle
zenginleştiren bir tasarım desenidir. Üç adımdan oluşur: Getirme (Retrieve),
Zenginleştirme (Augment) ve Üretme (Generate).

Önce kullanıcının sorusuna en alakalı belge parçaları bulunur. Ardından bu parçalar
modelin istemine bağlam olarak eklenir. Son olarak model, bu bağlama dayanarak cevabı
üretir.

RAG'in en önemli faydası, cevapların kendi verilerinize dayanması ve böylece
halüsinasyonun azalmasıdır. Ayrıca cevaplarda kaynak gösterilmesini mümkün kılar.

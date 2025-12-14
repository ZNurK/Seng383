<<<<<<< HEAD
# Seng383
=======
# Görev ve Dilek Yönetim Sistemi

Bu proje, çocuklar için görev ve dilek yönetim sistemidir. GUI formatından web formatına dönüştürülmüştür.

## Özellikler

- ✅ Görev ekleme (Öğretmen/Veli tarafından)
- ✅ Görev tamamlama
- ✅ Görev değerlendirme ve coin ödülü
- ✅ Dilek ekleme
- ✅ Dilek onaylama/reddetme
- ✅ Seviye şartlı (ör. Level 3) otomatik dilek onayı planlama
- ✅ Günlük ve haftalık görev listeleme
- ✅ Bütçe (coin) ve seviye takibi

## Gereksinimler

- Java 17 veya üzeri
- Maven 3.6 veya üzeri

## Kurulum ve Çalıştırma

### 1. Projeyi Klonlayın veya İndirin

### 2. Maven ile Bağımlılıkları İndirin

```bash
mvn clean install
```

### 3. Uygulamayı Çalıştırın

```bash
mvn spring-boot:run
```

veya

```bash
java -jar target/task-wish-manager-1.0.0.jar
```

### 4. Web Arayüzüne Erişin

Tarayıcınızda şu adrese gidin:
```
http://localhost:8080
```

## Kullanım

1. **Görevler Sekmesi**: Tüm görevleri görüntüleyin, tamamlayın ve değerlendirin
2. **Dilekler Sekmesi**: Tüm dilekleri görüntüleyin ve onaylayın/reddedin
3. **Görev Ekle Sekmesi**: Yeni görev ekleyin
4. **Dilek Ekle Sekmesi**: Yeni dilek ekleyin

## API Endpoints

### Görevler
- `GET /api/tasks/all` - Tüm görevleri listele
- `GET /api/tasks/daily` - Günlük görevleri listele
- `GET /api/tasks/weekly` - Haftalık görevleri listele
- `POST /api/tasks/add` - Yeni görev ekle
- `POST /api/tasks/{taskId}/complete` - Görevi tamamla
- `POST /api/tasks/{taskId}/check` - Görevi değerlendir

### Dilekler
- `GET /api/wishes/all` - Tüm dilekleri listele
- `POST /api/wishes/add` - Yeni dilek ekle
- `POST /api/wishes/{wishId}/check` - Dileği onayla/reddet

### Durum
- `GET /api/status/budget` - Bütçeyi görüntüle
- `GET /api/status/level` - Seviyeyi görüntüle
- `POST /api/status/add-coin` - Coin ekle

## Proje Yapısı

```
src/
├── main/
│   ├── java/
│   │   └── com/taskmanager/
│   │       ├── Application.java          # Spring Boot ana sınıf
│   │       ├── config/                   # Yapılandırma sınıfları
│   │       ├── controller/               # REST API controller'ları
│   │       ├── model/                    # Veri modeli sınıfları
│   │       └── service/                  # İş mantığı servisleri
│   └── resources/
│       ├── static/                       # Frontend dosyaları
│       │   ├── index.html
│       │   ├── style.css
│       │   └── app.js
│       └── application.properties        # Uygulama yapılandırması
└── pom.xml                               # Maven yapılandırması
```

## Notlar

- Uygulama başlatıldığında `Tasks.txt` ve `Wishes.txt` dosyalarından veri yüklenir (varsa)
- Tüm veriler hafızada tutulur ve dosyalara otomatik olarak kaydedilir
- CORS tüm kaynaklara açıktır (geliştirme için)

## Lisans

Bu proje eğitim amaçlıdır.

>>>>>>> 5d88c27 (Initial commit)

class Event {
  final int id;
  final String name;
  final String date;
  final String package;
  final String location;
  final String? description;
  final String? coverImage;
  final Map<String, dynamic>? settings;

  Event({
    required this.id,
    required this.name,
    required this.date,
    required this.package,
    required this.location,
    this.description,
    this.coverImage,
    this.settings,
  });

  factory Event.fromJson(Map<String, dynamic> json) {
    return Event(
      id: json['id'],
      name: json['name'],
      date: json['date'],
      package: json['package'],
      location: json['location'] ?? '',
      description: json['description'],
      coverImage: json['cover_image'],
      settings: json['settings'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'date': date,
      'package': package,
      'location': location,
      'description': description,
      'cover_image': coverImage,
      'settings': settings,
    };
  }
}

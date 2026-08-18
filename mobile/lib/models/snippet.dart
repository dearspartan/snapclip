class Snippet {
  final String id;
  final String name;
  final String text;
  final String category;
  final bool favorite;
  final DateTime createdAt;
  final DateTime updatedAt;

  Snippet({
    required this.id,
    required this.name,
    required this.text,
    required this.category,
    this.favorite = false,
    DateTime? createdAt,
    DateTime? updatedAt,
  })  : createdAt = createdAt ?? DateTime.now(),
        updatedAt = updatedAt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'text': text,
      'category': category,
      'favorite': favorite ? 1 : 0,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  factory Snippet.fromMap(Map<String, dynamic> map) {
    return Snippet(
      id: map['id'] as String,
      name: map['name'] as String,
      text: map['text'] as String,
      category: map['category'] as String,
      favorite: (map['favorite'] as int) == 1,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
    );
  }

  Snippet copyWith({
    String? id,
    String? name,
    String? text,
    String? category,
    bool? favorite,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Snippet(
      id: id ?? this.id,
      name: name ?? this.name,
      text: text ?? this.text,
      category: category ?? this.category,
      favorite: favorite ?? this.favorite,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

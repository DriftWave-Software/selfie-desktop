class SelfieImage {
  final String id;
  final String path;
  final String? appliedFilter;
  final String originalPath;

  SelfieImage({
    required this.id,
    required this.path,
    this.appliedFilter,
    required this.originalPath,
  });

  SelfieImage copyWith({
    String? id,
    String? path,
    String? appliedFilter,
    String? originalPath,
  }) {
    return SelfieImage(
      id: id ?? this.id,
      path: path ?? this.path,
      appliedFilter: appliedFilter ?? this.appliedFilter,
      originalPath: originalPath ?? this.originalPath,
    );
  }
}

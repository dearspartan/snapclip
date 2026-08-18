import '../models/snippet.dart';
import 'db_helper.dart';

class SnippetRepository {
  final DatabaseHelper _dbHelper = DatabaseHelper.instance;

  Future<List<Snippet>> getAllSnippets() async {
    final db = await _dbHelper.database;
    final maps = await db.query('snippets', orderBy: 'favorite DESC, updated_at DESC');
    return maps.map((map) => Snippet.fromMap(map)).toList();
  }

  Future<List<Snippet>> getFavorites() async {
    final db = await _dbHelper.database;
    final maps = await db.query(
      'snippets',
      where: 'favorite = ?',
      whereArgs: [1],
      orderBy: 'updated_at DESC',
    );
    return maps.map((map) => Snippet.fromMap(map)).toList();
  }

  Future<List<Snippet>> getSnippetsByCategory(String category) async {
    final db = await _dbHelper.database;
    final maps = await db.query(
      'snippets',
      where: 'category = ?',
      whereArgs: [category],
      orderBy: 'favorite DESC, updated_at DESC',
    );
    return maps.map((map) => Snippet.fromMap(map)).toList();
  }

  Future<List<Snippet>> searchSnippets(String query) async {
    if (query.trim().isEmpty) return getAllSnippets();
    final db = await _dbHelper.database;
    final q = '%${query.trim()}%';
    final maps = await db.query(
      'snippets',
      where: 'name LIKE ? OR text LIKE ? OR category LIKE ?',
      whereArgs: [q, q, q],
      orderBy: 'favorite DESC, updated_at DESC',
    );
    return maps.map((map) => Snippet.fromMap(map)).toList();
  }

  Future<int> insertSnippet(Snippet snippet) async {
    final db = await _dbHelper.database;
    return await db.insert('snippets', snippet.toMap());
  }

  Future<int> updateSnippet(Snippet snippet) async {
    final db = await _dbHelper.database;
    return await db.update(
      'snippets',
      snippet.toMap(),
      where: 'id = ?',
      whereArgs: [snippet.id],
    );
  }

  Future<int> deleteSnippet(String id) async {
    final db = await _dbHelper.database;
    return await db.delete(
      'snippets',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> toggleFavorite(String id, bool favorite) async {
    final db = await _dbHelper.database;
    return await db.update(
      'snippets',
      {'favorite': favorite ? 1 : 0, 'updated_at': DateTime.now().toIso8601String()},
      where: 'id = ?',
      whereArgs: [id],
    );
  }
}

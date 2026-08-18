import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../models/snippet.dart';
import '../utils/theme.dart';

class SnippetFormScreen extends StatefulWidget {
  final Snippet? snippet;

  const SnippetFormScreen({super.key, this.snippet});

  @override
  State<SnippetFormScreen> createState() => _SnippetFormScreenState();
}

class _SnippetFormScreenState extends State<SnippetFormScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _textController;
  late String _selectedCategory;
  late bool _isFavorite;

  final List<String> _categories = [
    'Personal',
    'College',
    'Work',
    'Development',
    'Forms',
    'Other'
  ];

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.snippet?.name ?? '');
    _textController = TextEditingController(text: widget.snippet?.text ?? '');
    _selectedCategory = widget.snippet?.category ?? 'Personal';
    _isFavorite = widget.snippet?.favorite ?? false;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _textController.dispose();
    super.dispose();
  }

  void _save() {
    if (_formKey.currentState!.validate()) {
      final now = DateTime.now();
      final snippet = Snippet(
        id: widget.snippet?.id ?? const Uuid().v4(),
        name: _nameController.text.trim(),
        text: _textController.text,
        category: _selectedCategory,
        favorite: _isFavorite,
        createdAt: widget.snippet?.createdAt ?? now,
        updatedAt: now,
      );
      Navigator.pop(context, snippet);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEditing = widget.snippet != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Edit Snippet' : 'Add Snippet'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check_rounded, color: AppTheme.primaryBlue, size: 28),
            onPressed: _save,
            tooltip: 'Save',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Snippet Name
              const Text('Snippet Name', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  hintText: 'e.g. Email Address, GitHub Token',
                ),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) {
                    return 'Please enter a snippet name';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),

              // Category Selection
              const Text('Category', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                value: _selectedCategory,
                decoration: const InputDecoration(),
                items: _categories.map((cat) {
                  return DropdownMenuItem(value: cat, child: Text(cat));
                }).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedCategory = val);
                },
              ),
              const SizedBox(height: 20),

              // Snippet Text Content
              const Text('Text Snippet', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
              const SizedBox(height: 8),
              TextFormField(
                controller: _textController,
                maxLines: 6,
                keyboardType: TextInputType.multiline,
                style: const TextStyle(fontFamily: 'monospace'),
                decoration: const InputDecoration(
                  hintText: 'Enter text content to paste automatically...',
                ),
                validator: (val) {
                  if (val == null || val.isEmpty) {
                    return 'Snippet content cannot be empty';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),

              // Favorite Checkbox
              SwitchListTile(
                contentPadding: EdgeInsets.zero,
                activeColor: AppTheme.primaryBlue,
                title: const Text('Mark as Favorite', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                subtitle: const Text('Favorite snippets appear at the top of home screen'),
                value: _isFavorite,
                onChanged: (val) => setState(() => _isFavorite = val),
              ),

              const SizedBox(height: 30),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.primaryBlue,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onPressed: _save,
                  child: Text(
                    isEditing ? 'Save Changes' : 'Create Snippet',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

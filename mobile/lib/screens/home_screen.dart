import 'package:flutter/material.dart';
import '../models/snippet.dart';
import '../models/pairing_info.dart';
import '../database/snippet_repository.dart';
import '../services/pairing_service.dart';
import '../services/websocket_service.dart';
import '../widgets/connection_badge.dart';
import '../widgets/category_chip.dart';
import '../widgets/snippet_card.dart';
import '../utils/theme.dart';
import 'snippet_form_screen.dart';
import 'pairing_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final SnippetRepository _repo = SnippetRepository();
  final PairingService _pairingService = PairingService();
  final WebSocketService _wsService = WebSocketService();

  List<Snippet> _allSnippets = [];
  List<Snippet> _filteredSnippets = [];
  List<Snippet> _favorites = [];
  PairingInfo? _pairingInfo;
  DeviceConnectionStatus _connectionStatus = DeviceConnectionStatus.disconnected;

  String _searchQuery = '';
  String _selectedCategory = 'All';

  final List<String> _categories = [
    'All',
    'Personal',
    'College',
    'Work',
    'Development',
    'Forms',
    'Other'
  ];

  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _wsService.statusStream.listen((status) {
      if (mounted) setState(() => _connectionStatus = status);
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _wsService.dispose();
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    _pairingInfo = await _pairingService.getSavedPairing();
    if (_pairingInfo != null) {
      _wsService.init(_pairingInfo!);
    }
    await _refreshSnippets();
  }

  Future<void> _refreshSnippets() async {
    final list = await _repo.getAllSnippets();
    final favs = await _repo.getFavorites();
    setState(() {
      _allSnippets = list;
      _favorites = favs;
      _applyFilters();
    });
  }

  void _applyFilters() {
    List<Snippet> temp = _allSnippets;

    // Filter by Category
    if (_selectedCategory != 'All') {
      temp = temp.where((s) => s.category == _selectedCategory).toList();
    }

    // Filter by Search Query
    if (_searchQuery.trim().isNotEmpty) {
      final q = _searchQuery.trim().toLowerCase();
      temp = temp.where((s) =>
        s.name.toLowerCase().contains(q) ||
        s.text.toLowerCase().contains(q) ||
        s.category.toLowerCase().contains(q)
      ).toList();
    }

    _filteredSnippets = temp;
  }

  void _onSearchChanged(String val) {
    setState(() {
      _searchQuery = val;
      _applyFilters();
    });
  }

  void _onCategorySelected(String category) {
    setState(() {
      _selectedCategory = category;
      _applyFilters();
    });
  }

  Future<void> _handleTapSnippet(Snippet snippet) async {
    if (_connectionStatus != DeviceConnectionStatus.connected) {
      _showOfflineDialog();
      return;
    }

    // Send paste request to Windows PC
    final success = await _wsService.sendPaste(snippet.text);

    if (mounted) {
      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle_outline, color: Colors.white),
                const SizedBox(width: 10),
                Text('Pasted "${snippet.name}" to ${_pairingInfo?.pcName ?? "PC"}!'),
              ],
            ),
            backgroundColor: AppTheme.statusConnected,
            duration: const Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Paste failed. Check target application on PC.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showOfflineDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.wifi_off_rounded, color: Colors.red),
            SizedBox(width: 10),
            Text('Computer Unavailable'),
          ],
        ),
        content: const Text(
          'Make sure SnapClip Desktop is running on your Windows PC and both devices are connected to the same Wi-Fi network.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('OK'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              _openPairingScreen();
            },
            child: const Text('Check Connection'),
          ),
        ],
      ),
    );
  }

  Future<void> _openPairingScreen() async {
    final result = await Navigator.push<PairingInfo>(
      context,
      MaterialPageRoute(builder: (_) => PairingScreen(pairingService: _pairingService)),
    );
    if (result != null) {
      setState(() {
        _pairingInfo = result;
      });
      _wsService.updatePairing(result);
    }
  }

  Future<void> _addOrEditSnippet([Snippet? existing]) async {
    final result = await Navigator.push<Snippet>(
      context,
      MaterialPageRoute(builder: (_) => SnippetFormScreen(snippet: existing)),
    );
    if (result != null) {
      if (existing != null) {
        await _repo.updateSnippet(result);
      } else {
        await _repo.insertSnippet(result);
      }
      await _refreshSnippets();
    }
  }

  Future<void> _deleteSnippet(String id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Snippet?'),
        content: const Text('Are you sure you want to delete this snippet?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Delete', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _repo.deleteSnippet(id);
      await _refreshSnippets();
    }
  }

  Future<void> _toggleFavorite(Snippet snippet) async {
    await _repo.toggleFavorite(snippet.id, !snippet.favorite);
    await _refreshSnippets();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SnapClip'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: ConnectionBadge(
              status: _connectionStatus,
              pairingInfo: _pairingInfo,
              onTap: _openPairingScreen,
            ),
          ),
        ],
      ),
      body: CustomScrollView(
        slivers: [
          // 1. Search Bar & Favorites Header
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Search Input
                  TextField(
                    controller: _searchController,
                    onChanged: _onSearchChanged,
                    decoration: InputDecoration(
                      hintText: 'Search snippets, categories...',
                      prefixIcon: const Icon(Icons.search_rounded, color: AppTheme.textSecondary),
                      suffixIcon: _searchQuery.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear_rounded),
                              onPressed: () {
                                _searchController.clear();
                                _onSearchChanged('');
                              },
                            )
                          : null,
                    ),
                  ),

                  // Favorites Grid
                  if (_favorites.isNotEmpty && _searchQuery.isEmpty && _selectedCategory == 'All') ...[
                    const SizedBox(height: 20),
                    const Row(
                      children: [
                        Icon(Icons.star_rounded, color: Colors.amber, size: 20),
                        SizedBox(width: 6),
                        Text(
                          'Favorites',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      height: 85,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _favorites.length,
                        itemBuilder: (ctx, i) {
                          final fav = _favorites[i];
                          return Container(
                            width: 140,
                            margin: const EdgeInsets.only(right: 10),
                            child: Card(
                              color: AppTheme.lightBlueBg,
                              child: InkWell(
                                onTap: () => _handleTapSnippet(fav),
                                borderRadius: BorderRadius.circular(16),
                                child: Padding(
                                  padding: const EdgeInsets.all(10.0),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Text(
                                        fav.name,
                                        style: const TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 13,
                                          color: AppTheme.darkBlue,
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        fav.text,
                                        style: const TextStyle(
                                          fontSize: 11,
                                          color: AppTheme.textSecondary,
                                          fontFamily: 'monospace',
                                        ),
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ],

                  // Categories Filter Chips
                  const SizedBox(height: 20),
                  const Text(
                    'Categories',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                  ),
                  const SizedBox(height: 10),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: _categories.map((cat) {
                        return CategoryChip(
                          label: cat,
                          isSelected: _selectedCategory == cat,
                          onTap: () => _onCategorySelected(cat),
                        );
                      }).toList(),
                    ),
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),

          // 2. Snippet Card List
          _filteredSnippets.isEmpty
              ? SliverFillRemaining(
                  hasScrollBody: false,
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.snippet_folder_outlined, size: 64, color: Colors.grey.shade400),
                        const SizedBox(height: 12),
                        Text(
                          _searchQuery.isNotEmpty
                              ? 'No snippets match "$_searchQuery"'
                              : 'No snippets in $_selectedCategory',
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 15),
                        ),
                      ],
                    ),
                  ),
                )
              : SliverPadding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  sliver: SliverList(
                    delegate: SliverChildBuilderDelegate(
                      (ctx, i) {
                        final snippet = _filteredSnippets[i];
                        return SnippetCard(
                          snippet: snippet,
                          onTap: () => _handleTapSnippet(snippet),
                          onFavoriteToggle: () => _toggleFavorite(snippet),
                          onEdit: () => _addOrEditSnippet(snippet),
                          onDelete: () => _deleteSnippet(snippet.id),
                        );
                      },
                      childCount: _filteredSnippets.length,
                    ),
                  ),
                ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _addOrEditSnippet(),
        icon: const Icon(Icons.add_rounded),
        label: const Text('Add Snippet'),
      ),
    );
  }
}

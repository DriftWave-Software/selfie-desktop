import 'dart:io';
import 'package:flutter/material.dart';
import 'package:photofilters/photofilters.dart';
import '../models/selfie_image.dart';

class FilterSelector extends StatefulWidget {
  final SelfieImage image;
  final Function(String) onFilterSelected;
  final VoidCallback onCancel;

  const FilterSelector({
    super.key,
    required this.image,
    required this.onFilterSelected,
    required this.onCancel,
  });

  @override
  State<FilterSelector> createState() => _FilterSelectorState();
}

class _FilterSelectorState extends State<FilterSelector> {
  List<Filter> filters = presetFiltersList;
  String selectedFilterId = '';

  @override
  void initState() {
    super.initState();
    selectedFilterId = widget.image.appliedFilter ?? '';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 300,
      decoration: BoxDecoration(
        color: Colors.black.withValues(red: 0, green: 0, blue: 0, alpha: 229), // 0.9 opacity
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(16.0),
          topRight: Radius.circular(16.0),
        ),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Select Filter',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: Colors.white,
                      ),
                ),
                Row(
                  children: [
                    TextButton(
                      onPressed: () {
                        widget.onFilterSelected(selectedFilterId);
                        widget.onCancel();
                      },
                      child: const Text(
                        'Apply',
                        style: TextStyle(color: Colors.green),
                      ),
                    ),
                    TextButton(
                      onPressed: widget.onCancel,
                      child: const Text(
                        'Cancel',
                        style: TextStyle(color: Colors.red),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Expanded(
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: filters.length,
              itemBuilder: (BuildContext context, int index) {
                return _buildFilterThumbnail(filters[index]);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterThumbnail(Filter filter) {
    final isSelected = selectedFilterId == filter.name;

    return GestureDetector(
      onTap: () {
        setState(() {
          selectedFilterId = filter.name;
        });
      },
      child: Container(
        margin: const EdgeInsets.all(8.0),
        width: 100,
        decoration: BoxDecoration(
          border: Border.all(
            color: isSelected ? Colors.white : Colors.transparent,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(8.0),
        ),
        child: Column(
          children: [
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(6),
                  topRight: Radius.circular(6),
                ),
                child: _buildFilteredImage(filter),
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(vertical: 4.0),
              width: double.infinity,
              decoration: BoxDecoration(
                color: isSelected ? Colors.white : Colors.grey[800],
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(6),
                  bottomRight: Radius.circular(6),
                ),
              ),
              child: Text(
                filter.name,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: isSelected ? Colors.black : Colors.white,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFilteredImage(Filter filter) {
    // In a real app, you would apply the filter to the image here
    // For demonstration, we'll just show the original image
    // PhotoFilter library can be used to apply the filter
    return Image.file(
      File(widget.image.path),
      fit: BoxFit.cover,
    );
  }
}

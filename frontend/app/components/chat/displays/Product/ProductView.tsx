"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ProductPayload } from "@/app/types/displays";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { PiCamera, PiShoppingCart } from "react-icons/pi";

interface ProductViewProps {
  product: ProductPayload;
}

const ProductView: React.FC<ProductViewProps> = ({ product }) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Detect if this is a book (has author field)
  const isBook = Boolean(product.author);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(price);
  };

  const formatPages = (pages: number) => {
    return `${pages} pages`;
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={`star-${i}`}
        className={`text-base ${
          i < Math.round(rating) ? "text-amber-400" : "text-secondary/30"
        }`}
      >
        ★
      </span>
    ));
  };

  const getTagColor = (tag: string) => {
    const tagLower = tag.toLowerCase();

    // Historical periods - amber/yellow tones
    if (
      tagLower.includes("wwii") ||
      tagLower.includes("ww2") ||
      tagLower.includes("cold war") ||
      tagLower.includes("vietnam") ||
      tagLower.includes("korean war") ||
      tagLower.includes("gulf war") ||
      tagLower.includes("post-war") ||
      tagLower.includes("interwar")
    ) {
      return "bg-amber-500/20 text-amber-300 border-amber-500/30";
    }

    // Intelligence/History topics - blue tones
    if (
      tagLower.includes("intelligence") ||
      tagLower.includes("history") ||
      tagLower.includes("espionage") ||
      tagLower.includes("spy") ||
      tagLower.includes("secret") ||
      tagLower.includes("classified")
    ) {
      return "bg-blue-500/20 text-blue-300 border-blue-500/30";
    }

    // Research/Analysis types - green tones
    if (
      tagLower.includes("osint") ||
      tagLower.includes("research") ||
      tagLower.includes("analysis") ||
      tagLower.includes("investigation") ||
      tagLower.includes("study")
    ) {
      return "bg-green-500/20 text-green-300 border-green-500/30";
    }

    // Military/Operations - red tones
    if (
      tagLower.includes("military") ||
      tagLower.includes("operation") ||
      tagLower.includes("combat") ||
      tagLower.includes("warfare")
    ) {
      return "bg-red-500/20 text-red-300 border-red-500/30";
    }

    // Geopolitical/Regions - purple tones
    if (
      tagLower.includes("soviet") ||
      tagLower.includes("russia") ||
      tagLower.includes("china") ||
      tagLower.includes("geopolitical") ||
      tagLower.includes("diplomatic")
    ) {
      return "bg-purple-500/20 text-purple-300 border-purple-500/30";
    }

    // Default - gray/slate
    return "bg-slate-500/20 text-slate-300 border-slate-500/30";
  };

  return (
    <motion.div
      className="w-full"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.4, 0, 0.2, 1] }}
    >
      {/* Single full-width card */}
      <div
        className="relative w-full rounded-xl overflow-hidden
          border-l-4 border-gray-500/40
          bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent
          backdrop-blur-sm shadow-lg"
      >
        {/* Book Cover Image - ON TOP, centered */}
        <div className="flex justify-center bg-background/30 p-6">
          <div className="relative w-64 lg:w-80 aspect-[2/3] overflow-hidden rounded-lg shadow-xl flex-shrink-0">
            {!imageLoaded && !imageError && (
              <Skeleton className="absolute inset-0 w-full h-full" />
            )}

            {!imageError && (
              <motion.img
                src={product.image}
                alt={product.name}
                className={`w-full h-full object-cover transition-all duration-500 ${
                  imageLoaded ? "opacity-100" : "opacity-0"
                }`}
                onLoad={() => setImageLoaded(true)}
                onError={() => {
                  setImageError(true);
                  setImageLoaded(true);
                }}
                loading="lazy"
              />
            )}

            {imageError && (
              <div className="absolute inset-0 flex items-center justify-center bg-foreground/50">
                <div className="text-secondary/50 text-center p-4">
                  <PiCamera className="text-4xl mx-auto mb-2 opacity-50" />
                  <div className="text-xs">No cover</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Book Info - BELOW image */}
        <div className="p-5 space-y-4">
          {/* Author */}
          {(isBook ? product.author : product.brand) && (
            <p className="text-xs text-primary/60 uppercase tracking-widest font-medium text-center">
              {isBook ? product.author : product.brand}
            </p>
          )}

          {/* Title */}
          <h1 className="text-2xl lg:text-3xl font-bold text-primary leading-tight text-center">
            {product.name}
          </h1>

          {/* Rating */}
          {product.rating && (
            <div className="flex items-center justify-center gap-2">
              <div className="flex">{renderStars(product.rating)}</div>
              <span className="text-xs text-primary/60">
                {product.rating.toFixed(1)}
              </span>
            </div>
          )}

          {/* Description */}
          <div className="bg-background/40 rounded-lg p-4 border border-foreground_alt/20">
            <p className="text-sm text-primary/90 leading-relaxed">
              {product.description}
            </p>
          </div>

          {/* Pages/Price + Year - Secondary metadata */}
          <div className="flex items-center justify-center gap-3">
            <span className="text-sm text-primary/60">
              {isBook && product.pages
                ? formatPages(product.pages)
                : product.price
                  ? formatPrice(product.price)
                  : "—"}
            </span>
            {product.year && (
              <Badge className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs px-2 py-0.5">
                {product.year}
              </Badge>
            )}
          </div>

          {/* Book Details - Inline grid */}
          {isBook && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
              {product.publisher && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Publisher</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.publisher}</p>
                </div>
              )}
              {product.language && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Language</p>
                  <p className="text-xs text-primary/90 font-medium">{product.language}</p>
                </div>
              )}
              {product.isbn_13 && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">ISBN-13</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.isbn_13}</p>
                </div>
              )}
              {product.isbn_10 && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">ISBN-10</p>
                  <p className="text-xs text-primary/90 font-medium">{product.isbn_10}</p>
                </div>
              )}
              {product.series && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Series</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.series}</p>
                </div>
              )}
            </div>
          )}

          {/* Product Details (non-book) - Inline grid */}
          {!isBook && (
            <div className="grid grid-cols-3 gap-3 text-center">
              {product.collection && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Collection</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.collection}</p>
                </div>
              )}
              {product.category && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Category</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.category}</p>
                </div>
              )}
              {product.subcategory && (
                <div className="bg-background/30 rounded-lg p-2 border border-foreground_alt/10">
                  <p className="text-xs text-primary/50">Type</p>
                  <p className="text-xs text-primary/90 font-medium truncate">{product.subcategory}</p>
                </div>
              )}
            </div>
          )}

          {/* Buy Link for Books - Prominent CTA */}
          {isBook && product.buy_link && (
            <div className="flex justify-center pt-4 pb-3">
              <a
                href={product.buy_link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-5 py-2.5
                  bg-alt_color_b/10 hover:bg-alt_color_b/20
                  text-alt_color_b font-semibold
                  rounded-lg transition-all duration-300
                  border border-alt_color_b
                  hover:scale-105"
              >
                <PiShoppingCart className="text-lg" />
                <span className="text-xs uppercase tracking-wide">Buy Now</span>
              </a>
            </div>
          )}

          {/* Tags - Colored badges */}
          {product.tags &&
            Array.isArray(product.tags) &&
            product.tags.length > 0 && (
              <div className="flex flex-wrap justify-center gap-1.5 pt-1">
                {product.tags.map((tag) => (
                  <Badge
                    key={tag}
                    className={`${getTagColor(tag)} border text-xs px-2 py-0.5`}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            )}
        </div>
      </div>
    </motion.div>
  );
};

export default ProductView;

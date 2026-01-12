"use client";

import React, { useState } from "react";
import { motion, Variants } from "framer-motion";
import { ProductPayload } from "@/app/types/displays";
import { Skeleton } from "@/components/ui/skeleton";
import { PiCamera } from "react-icons/pi";

interface ProductCardProps {
  product: ProductPayload;
  handleOpen: (product: ProductPayload) => void;
  index?: number;
}

const ProductCard: React.FC<ProductCardProps> = ({
  product,
  handleOpen,
  index = 0,
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  // Detect if this is a book (has author field)
  const isBook = Boolean(product.author);

  const cardVariants: Variants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.95,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        delay: index * 0.03,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  const renderStars = (rating: number) => {
    const fullStars = Math.round(rating);
    return (
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }, (_, i) => (
          <span
            key={`star-${i}`}
            className={`text-xs ${
              i < fullStars ? "text-amber-400" : "text-primary/30"
            }`}
          >
            ★
          </span>
        ))}
        <span className="text-xs text-primary/60 ml-1">
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="group relative w-full h-full"
      data-ref-id={product._REF_ID}
    >
      {/* Design System Card: border-l-4, gradient background, backdrop-blur, shadow-lg */}
      <div
        className="relative flex flex-col h-full rounded-xl overflow-hidden cursor-pointer
          border-l-4 border-gray-500/40 hover:border-gray-500/60
          bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent
          backdrop-blur-sm shadow-lg hover:shadow-xl
          transition-all duration-300 ease-in-out"
        onClick={() => handleOpen(product)}
      >
        {/* Image Container - Clean book cover without overlays */}
        <div className="relative w-full aspect-[2/3] overflow-hidden bg-background/50 flex-shrink-0">
          {!imageLoaded && !imageError && (
            <Skeleton className="absolute inset-0 w-full h-full" />
          )}

          {!imageError && (
            <motion.img
              src={product.image}
              alt={product.name}
              className={`w-full h-full object-cover transition-all duration-500 group-hover:scale-105 ${
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
                <PiCamera className="text-2xl mx-auto mb-1" />
                <div className="text-[9px]">No cover</div>
              </div>
            </div>
          )}
        </div>

        {/* Content Container - Minimal info below image */}
        <div className="flex flex-col p-3 gap-2 min-w-0 flex-1">
          {/* Title */}
          <h3 className="text-sm font-medium text-primary line-clamp-2 leading-snug">
            {product.name}
          </h3>

          {/* Author (for books) or Brand */}
          {(isBook ? product.author : product.brand) && (
            <p className="text-xs text-primary/60 truncate">
              {isBook ? product.author : product.brand}
            </p>
          )}

          {/* Bottom row: Pages/Price + Rating */}
          <div className="flex items-center justify-between mt-auto pt-1">
            <span className="text-xs font-semibold text-primary">
              {isBook && product.pages
                ? `${product.pages} pages`
                : product.price
                  ? `$${product.price}`
                  : ""}
            </span>
            {product.rating && renderStars(product.rating)}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ProductCard;

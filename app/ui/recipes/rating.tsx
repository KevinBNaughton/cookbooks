"use client";

import React, { useState } from "react";
import { Rating } from "react-simple-star-rating";
import clsx from "clsx";

export default function RecipeRating({
  initial_rating = 0,
  readonly = false,
  is_rtl = false,
}: {
  initial_rating: number;
  readonly: boolean;
  is_rtl: boolean;
}) {
  const [rating, setRating] = useState(0);

  // Catch Rating value
  const handleRating = (rate: number) => {
    setRating(rate);
  };
  // Optinal callback functions
  // const onPointerEnter = () => console.log("Enter");
  // const onPointerLeave = () => console.log("Leave");
  //  const onPointerMove = (value: number, index: number) =>
  //   console.log(value, index);

  return (
    <Rating
      initialValue={initial_rating / 2.0}
      readonly={readonly}
      size={20}
      onClick={handleRating}
      // onPointerEnter={onPointerEnter}
      // onPointerLeave={onPointerLeave}
      // onPointerMove={onPointerMove}
      className={clsx("flex flex-row")}
      style={{ display: "inline" }}
      SVGstyle={{ display: "inline" }}
      allowFraction
      showTooltip
      tooltipDefaultText={"no rating"}
      rtl={is_rtl}
      tooltipArray={[
        "Puke",
        "Puke+",
        "Bad",
        "Bad+",
        "Average",
        "Average+",
        "Great",
        "Great+",
        "Awesome",
        "Kevin LOVES!",
      ]}
      tooltipClassName={clsx("text-xs")}
      transition
    />
  );
}
